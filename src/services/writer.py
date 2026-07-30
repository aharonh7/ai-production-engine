import time
from datetime import datetime
from pathlib import Path
import yaml

class BookWriter:
    def __init__(self, project, provider_registry, config):
        self.project = project
        self.provider_registry = provider_registry
        self.config = config
        self.chapters = []

    def _get_provider_for_skill(self, skill_name):
        provider_name = self.config.get("skill_provider_mapping", {}).get(skill_name, "deepseek")
        provider = self.provider_registry.get(provider_name)
        if not provider:
            raise Exception(f"ספק {provider_name} לא נמצא עבור {skill_name}")
        return provider

    def write_book(self):
        print(f"\n📖 מתחיל כתיבה אמיתית: {self.project.name}")

        # 1. סיווג
        print("🔍 סיווג פרויקט...")
        provider = self._get_provider_for_skill("classify_project")
        classification = provider.generate(f"סטס את הפרויקט הזה: {self.project.description[:200]}")
        print(f"   ✅ סווג: {classification.content[:100]}")

        # 2. מתווה
        print("📋 יצירת מתווה...")
        provider = self._get_provider_for_skill("create_outline")
        outline_prompt = f"צור מתווה לספר מסוג {self.project.book_type} על: {self.project.description[:300]}"
        outline = provider.generate(outline_prompt)
        print(f"   ✅ מתווה נוצר")

        # 3. כתיבת פרקים
        print("✍️ כתיבת פרקים...")
        chapters = ["הקדמה", "פרק 1", "פרק 2", "סיכום"]
        full_content = f"# {self.project.name}\n\n"

        # קביעת טווח המילים מתוך הפרויקט
        min_words = self.project.min_words or 300
        max_words = self.project.max_words or 500

        for i, title in enumerate(chapters, 1):
            print(f"   📝 כותב: {title}")
            provider = self._get_provider_for_skill("write_chapter")
            
            # הוראה מפורשת לכתיבת סיפור בלבד, עם טווח המילים
            prompt = (
                f"Write only the story itself. No introduction, no summary, no extra text. "
                f"The story must be between {min_words} and {max_words} words total. "
                f"Write the following part: {title} for a children's book. "
                f"Story concept: {self.project.description[:200]}"
            )
            chapter_content = provider.generate(prompt)
            full_content += f"## {title}\n\n{chapter_content.content}\n\n"

            # עריכה
            print(f"   ✏️ עורך: {title}")
            provider = self._get_provider_for_skill("edit_chapter")
            edited = provider.generate(
                f"Edit this chapter for clarity and flow: {chapter_content.content}"
            )
            full_content += f"--- גרסה ערוכה ---\n\n{edited.content}\n\n"

        # 4. בדיקת המשכיות
        print("🔍 בודק המשכיות...")
        provider = self._get_provider_for_skill("continuity_check")
        continuity = provider.generate(
            f"Check for consistency in this text: {full_content[:500]}"
        )
        print(f"   ✅ בדיקה הושלמה")

        # 5. שמירה
        print("💾 שומר ספר...")
        output_dir = Path(__file__).parent.parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.project.name.replace(' ', '_')}_{timestamp}.md"
        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        print(f"   💾 נשמר: {file_path}")
        print("\n🎉 ספר אמיתי הושלם!")

        return full_content