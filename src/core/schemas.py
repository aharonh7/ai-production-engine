from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    name: str
    book_type: str = "novel"
    description: Optional[str] = None
    goal: Optional[str] = None
    target_audience: Optional[str] = None
    language: str = "he"
    budget_limit: float = 50.0
