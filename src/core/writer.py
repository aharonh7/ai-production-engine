import time
from datetime import datetime
from src.providers.registry import ProviderRegistry

class BookWriter:
    def __init__(self, project, provider):
        self.project = project
        self.provider = provider
        self.chapters_written = 0
        
    def write_book(self):
        print(f"\n📖 מתחיל כתיבת הספר: {self.project.name}")
        print(f"   סוג: {self.project.book_type}")
        print(f"   תיאור: {self.project.description[:100]}...\n")
        
        # 1. שלב סיווג
        print("🔍 שלב 1: סיווג הפרויקט...")
        classification = self._classify_project()
        print(f"   ✅ סווג כ: {classification.get('book_type', 'unknown')}")
        
        # 2. שלב תכנון
        print("\n📋 שלב 2: יצירת מתווה...")
        outline = self._create_outline(classification)
        print(f"   ✅ נוצר מתווה עם {len(outline.get('chapters', []))} פרקים")
        
        # 3. כתיבת פרקים
        print("\n✍️ שלב 3: כתיבת פרקים...")
        chapters = []
        for i, chapter in enumerate(outline.get('chapters', []), 1):
            print(f"   📝 כותב פרק {i}: {chapter.get('title', f'פרק {i}')}...")
            content = self._write_chapter(i, chapter)
            chapters.append({"number": i, "title": chapter.get('title', f'פרק {i}'), "content": content})
            print(f"   ✅ פרק {i} נכתב ({len(content.split())} מילים)")
            
            # עדכון התקדמות
            self.chapters_written = i
        
        # 4. הרכבת הספר
        print("\n📚 שלב 4: הרכבת הספר...")
        manuscript = self._assemble_manuscript(chapters)
        print(f"   ✅ הספר הורכב ({len(manuscript.split())} מילים)")
        
        # 5. שמירה
        print("\n💾 שלב 5: שמירת הספר...")
        self._save_manuscript(manuscript)
        print("   ✅ הספר נשמר!")
        
        print("\n🎉 סיימת! הספר מוכן.")
        return manuscript
    
    def _classify_project(self):
        """סיווג הפרויקט"""
        # symulacja (במציאות - קריאה ל-API)
        return {"book_type": self.project.book_type, "genre": "general"}
    
    def _create_outline(self, classification):
        """יצירת מתווה"""
        # שימוש ב-AI ליצירת מתווה
        prompt = f"צור מתווה לספר מסוג {classification.get('book_type')} על: {self.project.description[:200]}"
        response = self.provider.generate(prompt)
        # symulacja
        return {"chapters": [{"title": f"פרק {i}"} for i in range(1, 5)]}
    
    def _write_chapter(self, number, chapter):
        """כתיבת פרק בודד"""
        prompt = f"כתוב את פרק {number}: {chapter.get('title')} עבור הספר: {self.project.description[:200]}"
        response = self.provider.generate(prompt)
        return response.content
    
    def _assemble_manuscript(self, chapters):
        """הרכבת כל הפרקים לספר אחד"""
        manuscript = f"# {self.project.name}\n\n"
        for ch in chapters:
            manuscript += f"## {ch['title']}\n\n{ch['content']}\n\n"
        return manuscript
    
    def _save_manuscript(self, manuscript):
        """שמירת הספר"""
        import os
        from pathlib import Path
        output_dir = Path(__file__).parent.parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        file_path = output_dir / f"{self.project.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(manuscript)
        print(f"   💾 נשמר ב: {file_path}")