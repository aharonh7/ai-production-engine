from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.core.models import Project
from src.storage.repository import get_db
from src.core.registry import provider_registry, CONFIG
from src.orchestrator import PipelineOrchestrator
import uuid
from datetime import datetime
from pathlib import Path
import json
import os

router = APIRouter()

@router.post("/projects")
async def create_project(data: dict):
    try:
        print(f"📝 create_project התקבל: {data.get('name', 'no name')}")
        
        db = next(get_db())
        description = data.get("goal", "")
        source = data.get("source_content")
        if source:
            description += f"\n\n--- מקור ---\n{source[:5000]}\n--- סוף מקור ---"
        
        bible_content = data.get("bible_content", "")
        bible = bible_content if bible_content else None
        
        min_words = data.get("min_words", 300)
        max_words = data.get("max_words", 500)
        target_total_words_min = data.get("target_total_words_min", 3000)
        target_total_words_max = data.get("target_total_words_max", 5000)
        target_chapter_count = data.get("target_chapter_count", 5)
        target_words_per_chapter = data.get("target_words_per_chapter", 1000)
        
        project = Project(
            id=str(uuid.uuid4()),
            name=data.get("name", "פרויקט"),
            book_type=data.get("book_type", "novel"),
            description=description[:100000],
            state="draft",
            min_words=min_words,
            max_words=max_words,
            bible=bible,
            target_total_words_min=target_total_words_min,
            target_total_words_max=target_total_words_max,
            target_chapter_count=target_chapter_count,
            target_words_per_chapter=target_words_per_chapter
        )
        
        print(f"   ✅ פרויקט נוצר: {project.name}")
        
        db.add(project)
        db.commit()
        db.refresh(project)
        db.close()
        
        return {"id": project.id, "name": project.name, "state": project.state, "message": "✅ נוצר"}
    except Exception as e:
        print(f"❌ שגיאה ב-create_project: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects")
async def list_projects():
    try:
        db = next(get_db())
        projects = db.query(Project).all()
        db.close()
        return {"projects": [{"id": p.id, "name": p.name, "book_type": p.book_type, "state": p.state, "created_at": p.created_at.isoformat()} for p in projects]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    try:
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        db.close()
        if not project:
            raise HTTPException(status_code=404, detail="לא נמצא")
        return {
            "id": project.id, 
            "name": project.name, 
            "book_type": project.book_type, 
            "state": project.state, 
            "description": project.description,
            "bible": project.bible,
            "outline": project.outline,
            "current_chapter": project.current_chapter,
            "total_words": project.total_words
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    try:
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            db.close()
            raise HTTPException(status_code=404, detail="לא נמצא")
        db.delete(project)
        db.commit()
        db.close()
        return {"message": "✅ נמחק"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/run")
async def start_run(project_id: str, background_tasks: BackgroundTasks):
    try:
        print(f"🔥 start_run התקבל לפרויקט {project_id}")
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            db.close()
            raise HTTPException(status_code=404, detail="לא נמצא")
        
        if not project.bible:
            db.close()
            return {
                "error": "❌ אין Bible לפרויקט. אנא העלה בייבל לפני הפעלת ההפקה.",
                "project_id": project_id,
                "state": project.state
            }
        
        project.state = "active"
        db.commit()
        db.close()
        
        def run_pipeline():
            try:
                orchestrator = PipelineOrchestrator(project_id)
                orchestrator.run_book_pipeline()
                print(f"✅ Pipeline completed for {project_id}")
            except Exception as e:
                print(f"❌ Pipeline failed: {e}")
                import traceback
                traceback.print_exc()
                try:
                    db2 = next(get_db())
                    p = db2.query(Project).filter(Project.id == project_id).first()
                    if p:
                        p.state = "failed"
                        db2.commit()
                    db2.close()
                except:
                    pass
        
        background_tasks.add_task(run_pipeline)
        
        return {
            "project_id": project_id, 
            "state": "active", 
            "message": "✅ ההפקה החלה (פועל ברקע)"
        }
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"שגיאה: {str(e)}")

@router.get("/projects/{project_id}/status")
async def get_status(project_id: str):
    try:
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        db.close()
        if not project:
            raise HTTPException(status_code=404, detail="לא נמצא")
        
        return {
            "project_id": project_id,
            "state": project.state,
            "current_chapter": project.current_chapter,
            "total_words": project.total_words,
            "has_bible": bool(project.bible),
            "has_outline": bool(project.outline),
            "has_manuscript": bool(project.manuscript)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/manuscript")
async def get_manuscript(project_id: str):
    try:
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        db.close()
        if not project:
            raise HTTPException(status_code=404, detail="לא נמצא")
        
        if project.manuscript:
            return {
                "content": project.manuscript[:10000], 
                "word_count": len(project.manuscript.split()),
                "source": "database"
            }
        
        output_dir = Path(__file__).parent.parent.parent / "output"
        files = list(output_dir.glob(f"{project.name.replace(' ', '_')}*.md"))
        if files:
            with open(files[0], "r", encoding="utf-8") as f:
                content = f.read()
                return {"content": content[:10000], "word_count": len(content.split()), "source": "file"}
        return {"content": "טרם נכתב", "word_count": 0, "source": "none"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/budget")
async def get_budget():
    try:
        from src.core.registry import provider_registry
        adapter = provider_registry.get("deepseek")
        if adapter:
            status = adapter.get_status()
            return {
                "used": status.get("used", 0),
                "limit": status.get("limit", 2.0),
                "remaining": status.get("remaining", 2.0)
            }
        return {"error": "DeepSeek not found", "used": 0, "limit": 2.0, "remaining": 2.0}
    except Exception as e:
        return {"error": str(e), "used": 0, "limit": 2.0, "remaining": 2.0}
@router.get("/balance")
async def get_balance():
    try:
        import os
        import requests
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        
        if not api_key:
            return {"error": "❌ DeepSeek API key not found"}
        
        response = requests.get(
            "https://api.deepseek.com/user/balance",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("is_available") and data.get("balance_infos"):
                balance_info = data["balance_infos"][0]
                return {
                    "total_balance": balance_info.get("total_balance", "0.00"),
                    "topped_up": balance_info.get("topped_up_balance", "0.00"),
                    "granted": balance_info.get("granted_balance", "0.00"),
                    "currency": balance_info.get("currency", "USD"),
                    "status": "✅ זמין"
                }
            return {"error": "❌ לא נמצא מידע על יתרה"}
        else:
            return {"error": f"❌ שגיאה {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"❌ שגיאה: {str(e)}"}

@router.post("/projects/{project_id}/export")
async def export_project(project_id: str, data: dict = None):
    try:
        print(f"📦 ייצוא פרויקט {project_id}")
        
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        db.close()
        if not project:
            raise HTTPException(status_code=404, detail="פרויקט לא נמצא")
        
        content = project.manuscript
        
        if not content:
            output_dir = Path(__file__).parent.parent.parent / "output"
            files = list(output_dir.glob(f"{project.name.replace(' ', '_')}*.md"))
            if not files:
                raise HTTPException(status_code=404, detail="לא נמצא קובץ ספר")
            with open(files[0], "r", encoding="utf-8") as f:
                content = f.read()
        
        if not content or len(content.strip()) < 100:
            raise HTTPException(status_code=404, detail="הספר עדיין ריק")
        
        print(f"   ✅ תוכן נקרא ({len(content)} תווים)")
        
        from src.services.exporter import BookExporter
        exporter = BookExporter(project, content)
        format_type = data.get("format", "all") if data else "all"
        
        if format_type == "docx":
            file_path = exporter.export_docx()
            return {"format": "docx", "file": str(file_path), "message": "✅ DOCX נוצר"}
        elif format_type == "epub":
            file_path = exporter.export_epub()
            return {"format": "epub", "file": str(file_path), "message": "✅ EPUB נוצר"}
        elif format_type == "pdf":
            file_path = exporter.export_pdf()
            return {"format": "pdf", "file": str(file_path), "message": "✅ PDF נוצר"}
        else:
            results = exporter.export_all()
            return {"formats": list(results.keys()), "files": {k: str(v) for k, v in results.items()}, "message": "✅ כל הפורמטים נוצרו"}
    except Exception as e:
        print(f"❌ שגיאה בייצוא: {e}")
        raise HTTPException(status_code=500, detail=f"שגיאה: {str(e)}")

@router.post("/bible/parse")
async def parse_bible_endpoint(data: dict):
    try:
        from src.bible_parser import parse_bible
        bible_text = data.get("bible_content", "")
        if not bible_text:
            raise HTTPException(status_code=400, detail="No bible content")
        
        parsed = parse_bible(bible_text)
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/shutdown")
async def shutdown():
    """סוגר את השרת בכוח (לחצן 'יציאה' בממשק)."""
    import signal
    import threading

    def _kill():
        try:
            os.kill(os.getpid(), signal.SIGTERM)
        except Exception:
            pass
        # אם התהליך עדיין חי אחרי שנייה - סוגרים בכוח, ללא תנאים
        threading.Timer(2.0, lambda: os._exit(0)).start()

    threading.Timer(0.5, _kill).start()
    return {"message": "כבוי"}

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/projects/{project_id}/pause")
async def pause(): return {"status": "paused"}
@router.post("/projects/{project_id}/resume")
async def resume(): return {"status": "active"}
@router.post("/projects/{project_id}/stop")
async def stop(): return {"status": "stopped"}