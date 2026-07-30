from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.schemas import ProjectCreate, ProjectRead, RouteRead
from app.db.models import Project

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/projects", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.created_at.desc())))


@router.get("/providers/routes/{skill_id}", response_model=RouteRead)
def get_route(skill_id: str) -> RouteRead:
    from app.main import routing_service
    try:
        route = routing_service.route_for(skill_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RouteRead(
        skill_id=skill_id,
        provider=route.primary.provider,
        model=route.primary.model,
        fallback_provider=route.fallback.provider if route.fallback else None,
        fallback_model=route.fallback.model if route.fallback else None,
    )
