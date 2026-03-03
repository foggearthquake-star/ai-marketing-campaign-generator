"""Project endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from openai import AuthenticationError, RateLimitError
from sqlalchemy.orm import Session

from app.ai.llm_client import analyze_website
from app.db.session import get_db_session
from app.models.project import Project
from app.schemas.project import (
    ProjectAnalysisResponse,
    ProjectCreate,
    ProjectResponse,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db_session)) -> list[Project]:
    """Return all projects."""
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db_session)) -> Project:
    """Create and persist a project."""
    project = Project(name=payload.name, client_url=payload.client_url)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.post("/{project_id}/analyze", response_model=ProjectAnalysisResponse)
def analyze_project(project_id: int, db: Session = Depends(get_db_session)) -> ProjectAnalysisResponse:
    """Analyze project website URL with LLM and return structured output."""
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    if not project.client_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project client_url is missing.",
        )

    try:
        analysis = analyze_website(project.client_url)
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded.",
        ) from exc
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication with AI provider failed.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return ProjectAnalysisResponse(project_id=project.id, **analysis)
