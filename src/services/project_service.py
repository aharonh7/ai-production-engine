import asyncio
from src.core.writer import BookWriter

class ProjectService:
    def __init__(self, db, provider_registry):
        self.db = db
        self.provider_registry = provider_registry
    
    def start_production(self, project_id):
        """מתחיל את תהליך הפקת הספר"""
        from src.core.models import Project
        
        # שליפת הפרויקט
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception("פרויקט לא נמצא")
        
        # שליפת ה-Provider
        provider = self.provider_registry.get("deepseek")
        if not provider:
            raise Exception("DeepSeek לא מוגדר")
        
        print(f"\n{'='*50}")
        print(f"🚀 מתחיל הפקת ספר: {project.name}")
        print(f"{'='*50}\n")
        
        # יצירת כותב והרצה
        writer = BookWriter(project, provider)
        manuscript = writer.write_book()
        
        # עדכון סטטוס הפרויקט
        project.state = "completed"
        project.total_words = len(manuscript.split())
        self.db.commit()
        
        return {"status": "completed", "word_count": project.total_words}