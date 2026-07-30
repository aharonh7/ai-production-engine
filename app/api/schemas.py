from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    goal: str = Field(min_length=1)
    language: str = Field(min_length=2, max_length=40)
    book_type: str = "novel"
    settings: dict = Field(default_factory=dict)


class ProjectRead(ProjectCreate):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime


class RouteRead(BaseModel):
    skill_id: str
    provider: str
    model: str
    fallback_provider: str | None = None
    fallback_model: str | None = None
