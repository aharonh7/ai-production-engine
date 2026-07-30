from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "ai_production.db"

# ===== שימוש ב-NullPool =====
from sqlalchemy.pool import NullPool

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    poolclass=NullPool,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()