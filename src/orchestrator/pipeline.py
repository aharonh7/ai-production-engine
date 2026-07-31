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
    
    def _call_ai(self, prompt: str, system_prompt: str = None, max_tokens: int = 4096) -> str:
        print(f"   🤖 Calling AI...")
        response = self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.content
    
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
                parts = text.split(pattern)
                if len(parts) > 1:
                    text = parts[1].strip()
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith("Chapter") or line.strip().startswith("---"):
                            text = '\n'.join(lines[i+1:])
                            break
        
        if chapter_number and f"---CHAPTER {chapter_number}" in text:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(f"---CHAPTER {chapter_number}"):
                    text = '\n'.join(lines[i+1:])
                    break
        
        if "VERDICT:" in text or "ISSUES:" in text or "OVERALL NOTE:" in text:
            return ""
        
        return text.strip()
    
    def generate_outline(self) -> Dict:
        print("📋 Generating outline...")
        
        bible = self.project.bible or "{}"
        chapter_count = self.project.target_chapter_count or 5
        words_per_chapter = self.project.target_words_per_chapter or 1000
        
        prompt = OUTLINE_GENERATOR_PROMPT.format(
            bible=bible,
            chapter_count=chapter_count,
            words_per_chapter=words_per_chapter
        )
        
        response = self._call_ai(prompt)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                outline = json.loads(json_match.group())
                self.project.outline = json.dumps(outline, ensure_ascii=False)
                self._save_project()
                print(f"   ✅ Outline created with {len(outline.get('chapters', []))} chapters")
                return outline
        except:
            pass
        
        print("   ⚠️ Failed to parse outline, creating default")
        outline = {
            "chapters": [
                {
                    "number": i,
                    "title": f"Chapter {i}",
                    "purpose": "TBD",
                    "characters": [],
                    "key_beats": [],
                    "word_count_target": words_per_chapter,
                    "sets_up": []
                } for i in range(1, chapter_count + 1)
            ],
            "total_chapters": chapter_count,
            "total_word_count": chapter_count * words_per_chapter
        }
        self.project.outline = json.dumps(outline, ensure_ascii=False)
        self._save_project()
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
        
        response = self._call_ai(prompt)
        
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
                
                writer_response = self._call_ai(revise_prompt)
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
                
                writer_response = self._call_ai(revise_prompt)
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
        
        summaries = []
        for ch in self.chapters:
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