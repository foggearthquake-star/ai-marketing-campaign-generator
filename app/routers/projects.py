"""Project endpoints."""

import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from openai import AuthenticationError, RateLimitError
from sqlalchemy.orm import Session

from app.ai.llm_client import analyze_website
from app.core.config import OPENAI_MODEL
from app.db.session import get_db_session
from app.models.project import Project
from app.schemas.analysis import AnalysisListItemResponse
from app.schemas.project import (
    ProjectAnalysisResponse,
    ProjectCreate,
    ProjectResponse,
)
from app.services.analysis_service import AnalysisService

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


@router.post("/{project_id}/analyze", response_model=dict[str, int | str])
def analyze_project(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
) -> dict[str, int | str]:
    """Analyze project website URL with LLM and return structured output."""
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    if not project.client_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project client_url is missing.",
        )

    analysis_record = AnalysisService.create_analysis(db, project.id)

    background_tasks.add_task(
        AnalysisService.run_analysis,
        analysis_record.id,
    )
    return {
        "analysis_id": analysis_record.id,
        "status": analysis_record.status,
    }


@router.get("/{project_id}/analyses", response_model=list[AnalysisListItemResponse])
def list_project_analyses(project_id: int, db: Session = Depends(get_db_session)) -> list[AnalysisListItemResponse]:
    """Return all analyses for a project ordered by newest first."""
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return AnalysisService.get_analyses_by_project_id(db, project_id)
