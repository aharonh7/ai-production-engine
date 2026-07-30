from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def uuid_str() -> str:
    return str(uuid.uuid4())


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIGURING = "configuring"
    READY = "ready"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    book_type: Mapped[str] = mapped_column(String(50), default="novel")
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="queued")
    config_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OutputVersion(Base):
    __tablename__ = "output_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    job_id: Mapped[str | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    output_type: Mapped[str] = mapped_column(String(80), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    content_path: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    run_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    job_id: Mapped[str | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_micros: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
