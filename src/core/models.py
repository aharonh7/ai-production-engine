from sqlalchemy import Column, String, DateTime, Float, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def gen_id():
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    book_type = Column(String, default="novel")
    description = Column(Text, default="")
    state = Column(String, default="draft")
    total_cost = Column(Float, default=0.0)
    total_words = Column(Integer, default=0)
    min_words = Column(Integer, default=300)
    max_words = Column(Integer, default=500)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # ===== שדות בייבל =====
    bible = Column(Text, nullable=True)          # הבייבל המלא
    outline = Column(Text, nullable=True)        # מתווה פרקים
    manuscript = Column(Text, nullable=True)     # הספר המלא
    current_chapter = Column(Integer, default=0)
    story_state = Column(Text, nullable=True)
    
    # ===== שדות שנשאבים מהבייבל =====
    target_total_words_min = Column(Integer, default=3000)
    target_total_words_max = Column(Integer, default=5000)
    target_chapter_count = Column(Integer, default=5)
    target_words_per_chapter = Column(Integer, default=1000)
    
    # ===== שדות נוספים מהבייבל =====
    pov = Column(String, default="")
    tense = Column(String, default="")
    tone = Column(String, default="")
    characters = Column(Text, default="")        # JSON array
    setting = Column(Text, default="")
    core_promise = Column(Text, default="")
    one_sentence_pitch = Column(Text, default="")