"""
Pipeline Orchestrator - מנהל את תהליך הכתיבה המלא
"""
import json
import time
import re
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from src.core.models import Project
from src.storage.repository import get_db
from src.core.registry import provider_registry
from src.prompts import *
from src.orchestrator.story_state import StoryState


class PipelineOrchestrator:
    """מנהל את הפייפליין המלא - מכתיבת פרק ועד להגהה"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.project = self._load_project()
        self.story_state = StoryState(project_id, self.project.story_state)
        self.provider = provider_registry.get("deepseek")
        self.chapters = []
        self.total_words_all_chapters = 0
        
        if not self.provider:
            raise Exception("❌ DeepSeek not found - check API key")
    
    def _load_project(self) -> Project:
        db = next(get_db())
        project = db.query(Project).filter(Project.id == self.project_id).first()
        db.close()
        if not project:
            raise Exception(f"Project {self.project_id} not found")
        return project
    
    def _save_project(self):
        try:
            db = next(get_db())
            project = db.query(Project).filter(Project.id == self.project_id).first()
            if project:
                project.story_state = self.story_state.to_json()
                project.current_chapter = self.project.current_chapter
                project.state = self.project.state
                project.total_words = self.total_words_all_chapters
                project.manuscript = self.project.manuscript
                project.outline = self.project.outline
                db.commit()
            db.close()
        except Exception as e:
            print(f"⚠️ שגיאה בשמירה: {e}")
    
    def _estimate_max_tokens(self, word_target: int, include_notes: bool = False) -> int:
        """מחשב max_tokens בטוח ליעד מילים נתון, כדי לא לחתוך תשובות בספרים עם
        פרקים ארוכים. tokens_per_word=1.6 הוא מרווח ביטחון (מילה אנגלית ≈ 1.3 טוקן).
        include_notes=True מוסיף מקום להערות/החלטות עורך שמצורפות לטקסט המלא."""
        tokens_per_word = 1.6
        base = int(word_target * tokens_per_word)
        if include_notes:
            base = int(base * 1.4) + 400
        return min(max(base + 300, 1024), 8000)  # תקרה 8000 = המקסימום הנתמך ע"י DeepSeek

    def _call_ai(self, prompt: str, system_prompt: str = None, max_tokens: int = 4096) -> str:
        print(f"   🤖 Calling AI...")
        response = self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.7
        )
        if getattr(response, "was_truncated", False):
            print(f"   ⚠️ AI response was truncated (finish_reason=length, "
                  f"completion_tokens={response.completion_tokens}). Consider raising max_tokens.")
        return response.content

    def _call_ai_full(self, prompt: str, system_prompt: str = None, max_tokens: int = 4096):
        """כמו _call_ai, אבל מחזירה את אובייקט ה-ProviderResponse המלא (כולל finish_reason/was_truncated),
        לשימוש במקומות שצריכים לזהות חיתוך תשובה, כמו יצירת המתווה."""
        print(f"   🤖 Calling AI...")
        response = self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.7
        )
        if getattr(response, "was_truncated", False):
            print(f"   ⚠️ AI response was truncated (finish_reason=length, "
                  f"completion_tokens={response.completion_tokens}). Consider raising max_tokens.")
        return response
    
    def _extract_text_from_response(self, response: str, chapter_number: int = None) -> str:
        """חילוץ טקסט מתשובת AI"""
        text = response
        
        patterns = [
            "NEW ELEMENTS INTRODUCED:",
            "---REVISED CHAPTER",
            "---FINAL CHAPTER",
            "CORRECTED TEXT:",
            "REVISED CHAPTER:",
            "FINAL CHAPTER:",
            "---CHAPTER",
        ]
        
        for pattern in patterns:
            if pattern in text:
                parts = text.split(pattern, 1)
                if len(parts) > 1:
                    remainder = parts[1]
                    # השורה הראשונה מיד אחרי התבנית היא תמיד שורת הכותרת
                    # (למשל " 1: Chapter Title---") - תמיד מדלגים עליה, ותו לא.
                    # (הגרסה הקודמת חיפשה שורה שמתחילה ב-"Chapter" או "---" כדי
                    #  לזהות את שורת הכותרת, אבל אם שורת הכותרת בפועל לא מתחילה
                    #  באחד מאלה, הלולאה ממשיכה בטעות עד לשורת ה-"---" שסוגרת את
                    #  הפרק בסופו - וחותכת את כל תוכן הפרק.)
                    if '\n' in remainder:
                        _, text = remainder.split('\n', 1)
                    else:
                        text = ""
                    text = text.strip()
                # מספיקה התאמה אחת - לא ממשיכים לבדוק תבניות נוספות על טקסט
                # שכבר עבר עיבוד, כדי לא לחתוך שוב בטעות
                break
        
        if chapter_number and f"---CHAPTER {chapter_number}" in text:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(f"---CHAPTER {chapter_number}"):
                    text = '\n'.join(lines[i+1:])
                    break
        
        # מסירים שורת "---" בודדת שנשארת בסוף הטקסט (סוגר הפרק)
        lines = text.split('\n')
        while lines and lines[-1].strip() in ("---", ""):
            lines.pop()
        text = '\n'.join(lines)
        
        if "VERDICT:" in text or "ISSUES:" in text or "OVERALL NOTE:" in text:
            return ""
        
        return text.strip()
    
    def generate_outline(self) -> Dict:
        print("📋 Generating outline...")

        bible = self.project.bible or "{}"
        chapter_count = self.project.target_chapter_count or 5
        words_per_chapter = self.project.target_words_per_chapter or 1000

        # ===== צ'אנקים =====
        # ספרים עם הרבה פרקים (למשל 77) לא יכולים לקבל מתווה מפורט בקריאת AI
        # אחת - זה חורג בקלות ממגבלת הפלט של DeepSeek (עד 8K טוקנים). מייצרים
        # את המתווה בקבוצות של עד BATCH_SIZE פרקים בכל קריאה, ומאחדים בסוף.
        BATCH_SIZE = 15
        MAX_OUTPUT_TOKENS = 8000  # התקרה המרבית הנתמכת ע"י DeepSeek

        all_chapters = []
        chapter_start = 1
        while chapter_start <= chapter_count:
            chapter_end = min(chapter_start + BATCH_SIZE - 1, chapter_count)

            # הקשר קצר מהפרקים שכבר תוכננו, כדי לשמור על רצף עלילתי בין הצ'אנקים
            if all_chapters:
                context_lines = [
                    f"Chapter {c.get('number')}: {c.get('title', '')} — {c.get('purpose', '')}"
                    for c in all_chapters
                ]
                previous_chapters_context = (
                    "=== CHAPTERS ALREADY PLANNED (for continuity — do not repeat these beats) ===\n"
                    + "\n".join(context_lines)
                )
            else:
                previous_chapters_context = ""

            prompt = OUTLINE_GENERATOR_PROMPT.format(
                bible=bible,
                chapter_count=chapter_count,
                chapter_start=chapter_start,
                chapter_end=chapter_end,
                words_per_chapter=words_per_chapter,
                previous_chapters_context=previous_chapters_context
            )

            print(f"   📦 Outline batch: chapters {chapter_start}-{chapter_end} of {chapter_count}")
            response = self._call_ai_full(prompt, max_tokens=MAX_OUTPUT_TOKENS)

            if response.was_truncated:
                print(f"   ⚠️ Outline batch {chapter_start}-{chapter_end} response was TRUNCATED "
                      f"(finish_reason=length, completion_tokens={response.completion_tokens}). "
                      f"JSON parsing may fail for this batch.")

            try:
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if not json_match:
                    raise ValueError("No JSON object found in response")
                batch_data = json.loads(json_match.group())
                batch_chapters = batch_data.get("chapters", [])
                if not batch_chapters:
                    raise ValueError("Parsed JSON but 'chapters' list is empty")
                all_chapters.extend(batch_chapters)
                print(f"      ✅ Parsed {len(batch_chapters)} chapters for this batch")
            except Exception as e:
                print(f"      ❌ Failed to parse outline batch {chapter_start}-{chapter_end}: {e}")
                print(f"      ⚠️ Falling back to placeholder chapters for this batch only")
                for i in range(chapter_start, chapter_end + 1):
                    all_chapters.append({
                        "number": i,
                        "title": f"Chapter {i}",
                        "purpose": "TBD",
                        "characters": [],
                        "key_beats": [],
                        "word_count_target": words_per_chapter,
                        "sets_up": []
                    })

            chapter_start = chapter_end + 1

        # מספרים מחדש ברצף למקרה שה-AI לא החזיר number תואם, ומחשבים את הסכום בפייתון
        # (ולא בתוך הפרומפט - שם זה גרם לקריסה קודם, כי .format() לא תומך בביטויים חשבוניים)
        for idx, ch in enumerate(all_chapters, 1):
            ch["number"] = idx

        outline = {
            "chapters": all_chapters,
            "total_chapters": len(all_chapters),
            "total_word_count": len(all_chapters) * words_per_chapter
        }
        self.project.outline = json.dumps(outline, ensure_ascii=False)
        self._save_project()
        print(f"   ✅ Outline complete: {len(all_chapters)} chapters total")
        return outline
    
    def write_chapter(self, chapter_number: int, chapter_data: Dict) -> str:
        print(f"   ✍️ Writing chapter {chapter_number}: {chapter_data.get('title', f'Chapter {chapter_number}')}")
        
        bible = self.project.bible or "{}"
        outline = self.project.outline or "{}"
        story_state = self.story_state.to_json()
        chapter_summaries = self._get_chapter_summaries()
        
        target_words = self.project.target_words_per_chapter or 1000
        
        outline_instruction = ""
        if chapter_data.get('purpose'):
            outline_instruction = f"\n\nThis chapter's purpose is: {chapter_data.get('purpose')}"
        if chapter_data.get('key_beats'):
            outline_instruction += f"\nKey beats to include: {', '.join(chapter_data.get('key_beats', []))}"
        
        prompt = WRITER_PROMPT.format(
            chapter_number=chapter_number,
            chapter_title=chapter_data.get('title', f'Chapter {chapter_number}'),
            bible=bible,
            outline=outline,
            story_state=story_state,
            chapter_summaries=chapter_summaries,
            target_word_count=target_words,
            chapter_beat=chapter_data.get('purpose', 'TBD')
        )
        
        prompt += outline_instruction
        
        response = self._call_ai(prompt, max_tokens=self._estimate_max_tokens(target_words))
        chapter_text = self._extract_text_from_response(response, chapter_number)
        word_count = len(chapter_text.split())
        print(f"   📝 Chapter written: {word_count} words")
        
        self.chapters.append({
            "number": chapter_number,
            "title": chapter_data.get('title', f'Chapter {chapter_number}'),
            "text": chapter_text,
            "word_count": word_count
        })
        
        return chapter_text
    
    def _structural_edit(self, chapter_number: int, chapter_text: str) -> str:
        print(f"   🔍 Structural editing chapter {chapter_number}...")
        
        bible = self.project.bible or "{}"
        outline = self.project.outline or "{}"
        story_state = self.story_state.to_json()
        
        current_text = chapter_text
        max_rounds = 3
        
        for round_num in range(1, max_rounds + 1):
            prompt = STRUCTURAL_EDITOR_PROMPT.format(
                chapter_number=chapter_number,
                chapter_text=current_text,
                bible=bible,
                outline=outline,
                story_state=story_state
            )
            
            editor_response = self._call_ai(prompt)
            
            if "VERDICT: APPROVE" in editor_response:
                print(f"   ✅ Structural edit approved (round {round_num})")
                return current_text
            
            if "VERDICT: REVISE" in editor_response:
                print(f"   ⚠️ Editor found issues (round {round_num})")
                
                revise_prompt = WRITER_STRUCTURAL_RESPONSE_PROMPT.format(
                    chapter_number=chapter_number,
                    chapter_title=f"Chapter {chapter_number}",
                    chapter_text=current_text,
                    editor_notes=editor_response,
                    bible=bible,
                    outline=outline,
                    story_state=story_state
                )
                
                word_target = max(len(current_text.split()), self.project.target_words_per_chapter or 1000)
                writer_response = self._call_ai(revise_prompt, max_tokens=self._estimate_max_tokens(word_target, include_notes=True))
                revised_text = self._extract_text_from_response(writer_response)
                
                if not revised_text or len(revised_text.strip()) < 50:
                    print(f"      ⚠️ Writer returned empty response, keeping original")
                    return current_text
                
                if revised_text.strip() == current_text.strip():
                    print(f"      ⚠️ Writer rejected all changes, keeping original")
                    return current_text
                
                if len(revised_text.split()) < len(current_text.split()) * 0.3:
                    print(f"      ⚠️ Revised chapter too short, keeping original")
                    return current_text
                
                current_text = revised_text
                print(f"      ✅ Writer revised chapter ({len(revised_text.split())} words)")
        
        print(f"   ⚠️ Max rounds reached ({max_rounds})")
        return current_text
    
    def _language_edit(self, chapter_number: int, chapter_text: str) -> str:
        print(f"   ✏️ Language editing chapter {chapter_number}...")
        
        bible = self.project.bible or "{}"
        current_text = chapter_text
        max_rounds = 3
        
        for round_num in range(1, max_rounds + 1):
            prompt = LANGUAGE_EDITOR_PROMPT.format(
                chapter_text=current_text,
                bible=bible
            )
            
            editor_response = self._call_ai(prompt)
            
            if "VERDICT: APPROVE" in editor_response:
                print(f"   ✅ Language edit approved (round {round_num})")
                return current_text
            
            if "VERDICT: REVISE" in editor_response:
                print(f"   ⚠️ Editor found issues (round {round_num})")
                
                revise_prompt = WRITER_LANGUAGE_RESPONSE_PROMPT.format(
                    chapter_number=chapter_number,
                    chapter_title=f"Chapter {chapter_number}",
                    chapter_text=current_text,
                    editor_notes=editor_response
                )
                
                writer_response = self._call_ai(revise_prompt, max_tokens=self._estimate_max_tokens(max(len(current_text.split()), self.project.target_words_per_chapter or 1000), include_notes=True))
                revised_text = self._extract_text_from_response(writer_response)
                
                if not revised_text or len(revised_text.strip()) < 50:
                    print(f"      ⚠️ Writer returned empty response, keeping original")
                    return current_text
                
                if revised_text.strip() == current_text.strip():
                    print(f"      ⚠️ Writer rejected all changes, keeping original")
                    return current_text
                
                if len(revised_text.split()) < len(current_text.split()) * 0.3:
                    print(f"      ⚠️ Revised chapter too short, keeping original")
                    return current_text
                
                current_text = revised_text
                print(f"      ✅ Writer revised chapter ({len(revised_text.split())} words)")
        
        print(f"   ⚠️ Max rounds reached ({max_rounds})")
        return current_text
    
    def _update_story_state(self, chapter_number: int, chapter_text: str):
        print(f"   📝 Updating story state for chapter {chapter_number}...")
        
        existing_characters = list(self.story_state.data['characters'].keys())
        existing_characters_str = ", ".join(existing_characters) if existing_characters else "None yet"
        
        prompt = STORY_STATE_UPDATER_PROMPT.format(
            chapter_number=chapter_number,
            chapter_text=chapter_text[:3000],
            current_state=self.story_state.to_json()
        )
        
        prompt += f"\n\nIMPORTANT: Existing characters are: {existing_characters_str}. Do NOT change character names unless absolutely necessary. Keep the same names throughout the book."
        
        response = self._call_ai(prompt)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                new_state = json.loads(json_match.group())
                if "characters" in new_state:
                    for name, data in new_state["characters"].items():
                        self.story_state.update_character(name, data)
                if "open_threads" in new_state:
                    for thread in new_state["open_threads"]:
                        self.story_state.add_open_thread(thread, chapter_number)
                if "established_facts" in new_state:
                    for fact in new_state["established_facts"]:
                        self.story_state.add_established_fact(fact, chapter_number)
        except:
            pass
        
        print(f"   ✅ Story state updated")
    
    def _get_chapter_summaries(self) -> str:
        if not self.chapters:
            return "No previous chapters"

        # ===== הגבלת גודל =====
        # בספרים עם הרבה פרקים (למשל 77), תקציר מלא (200 מילים) מכל פרק שנכתב
        # עד כה היה מנפח את הפרומפט עד לחריגה ממגבלת הטוקנים לקראת סוף הספר.
        # רק ה-RECENT_FULL הפרקים האחרונים מקבלים תקציר מפורט; פרקים ישנים
        # יותר מקבלים רק כותרת, כדי לשמור על המשכיות בלי להתפוצץ בגודל.
        RECENT_FULL = 3

        summaries = []
        older = self.chapters[:-RECENT_FULL] if len(self.chapters) > RECENT_FULL else []
        recent = self.chapters[-RECENT_FULL:] if len(self.chapters) > RECENT_FULL else self.chapters

        if older:
            summaries.append("=== EARLIER CHAPTERS (titles only, for reference) ===")
            for ch in older:
                summaries.append(f"Chapter {ch['number']}: {ch['title']}")
            summaries.append("\n=== MOST RECENT CHAPTERS (detailed, for direct continuity) ===")

        for ch in recent:
            words = ch['text'].split()
            preview = ' '.join(words[:200])
            summaries.append(f"Chapter {ch['number']}: {ch['title']}\n{preview}...\n")

        return "\n".join(summaries)
    
    def _quality_check(self) -> bool:
        print("   🔍 Running quality check...")
        
        total_words = sum(ch['word_count'] for ch in self.chapters)
        
        if total_words < 100:
            print(f"   ❌ Quality check FAILED: Only {total_words} words")
            return False
        
        characters = set()
        for ch in self.chapters:
            text = ch['text']
            names = re.findall(r'\b([A-Z][a-z]+)\b', text)
            for name in names:
                if len(name) > 2 and name not in ['The', 'And', 'But', 'For', 'Not', 'Yet']:
                    characters.add(name)
        
        if len(characters) < 1:
            print(f"   ❌ Quality check FAILED: No characters found")
            return False
        
        print(f"   ✅ Quality check passed: {len(characters)} characters, {total_words} words")
        return True
    
    def run_book_pipeline(self):
        print(f"\n📖 Starting pipeline for: {self.project.name}")
        print(f"   Book type: {self.project.book_type}")
        print(f"   Target words per chapter: {self.project.target_words_per_chapter}")
        print(f"   Total chapters: {self.project.target_chapter_count}\n")
        
        outline = None
        if self.project.outline:
            try:
                outline = json.loads(self.project.outline)
                print(f"✅ Outline loaded: {len(outline.get('chapters', []))} chapters")
            except:
                pass
        
        if not outline:
            outline = self.generate_outline()
        
        chapters = outline.get('chapters', [])
        total_chapters = len(chapters)
        
        print(f"\n📝 Writing {total_chapters} chapters...\n")
        
        for i, chapter_data in enumerate(chapters, 1):
            print(f"\n--- Chapter {i} ---")
            
            chapter_text = self.write_chapter(i, chapter_data)
            chapter_text = self._structural_edit(i, chapter_text)
            chapter_text = self._language_edit(i, chapter_text)
            self._update_story_state(i, chapter_text)
            
            self.chapters[-1]['text'] = chapter_text
            self.chapters[-1]['word_count'] = len(chapter_text.split())
            
            self.total_words_all_chapters = sum(ch['word_count'] for ch in self.chapters)
            
            self.project.current_chapter = i
            self._save_project()
            
            print(f"   ✅ Chapter {i} completed ({self.chapters[-1]['word_count']} words)")
            print(f"   📌 Total so far: {self.total_words_all_chapters} words")
            print(f"   📌 Progress: {i}/{total_chapters}")
        
        print("\n📚 Assembling manuscript...")
        manuscript = self._assemble_manuscript()
        
        if not self._quality_check():
            print("   ❌ Quality check failed - book not saved")
            self.project.state = "failed"
            self._save_project()
            return None
        
        self.project.manuscript = manuscript
        self.total_words_all_chapters = len(manuscript.split())
        self.project.total_words = self.total_words_all_chapters
        self.project.state = "completed"
        self._save_project()
        
        print(f"\n✅ Book complete! {self.project.total_words} words")
        self._save_manuscript_file(manuscript)

        try:
            from src.services.exporter import BookExporter
            print("\n📦 Auto-exporting to DOCX / EPUB / PDF ...")
            BookExporter(self.project, manuscript).export_all()
        except Exception as e:
            # ייצוא אוטומטי הוא bonus - אם הוא נכשל (למשל תלות חסרה),
            # לא רוצים שזה יפיל את כל ריצת הכתיבה. ניתן תמיד לייצא
            # ידנית דרך כפתורי הייצוא בממשק לאחר מכן.
            print(f"   ⚠️ Auto-export failed (you can still export manually from the UI): {e}")

        return manuscript
    
    def _assemble_manuscript(self) -> str:
        manuscript = f"# {self.project.name}\n\n"
        for ch in self.chapters:
            manuscript += f"## {ch['title']}\n\n{ch['text']}\n\n"
        return manuscript
    
    def _save_manuscript_file(self, manuscript: str):
        output_dir = Path(__file__).parent.parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        file_path = output_dir / f"{self.project.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(manuscript)
        print(f"   💾 Saved to: {file_path}")