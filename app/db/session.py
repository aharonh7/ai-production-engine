from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings
from app.db.base import Base

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


def init_db() -> None:
    Base.metadata.create_all(engine)
