"""API v1 analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.analysis import Analysis
from app.models.job_run import JobRun
from app.models.project_workspace import ProjectWorkspace
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership

router = APIRouter(prefix="/analyses", tags=["v1-analyses"])


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: int,
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> dict:
    """Return analysis with v1 status metadata."""
    membership = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id, WorkspaceMembership.user_id == user.id)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Workspace access denied.")

    analysis = (
        db.query(Analysis)
        .join(ProjectWorkspace, ProjectWorkspace.project_id == Analysis.project_id)
        .filter(Analysis.id == analysis_id, ProjectWorkspace.workspace_id == workspace_id)
        .first()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    latest_job = (
        db.query(JobRun)
        .filter(JobRun.job_type == "analysis", JobRun.entity_id == analysis.id, JobRun.workspace_id == workspace_id)
        .order_by(JobRun.created_at.desc())
        .first()
    )
    return {
        "id": analysis.id,
        "project_id": analysis.project_id,
        "status": analysis.status,
        "structured_output": analysis.structured_output,
        "error_message": analysis.error_message,
        "model": analysis.model,
        "prompt_tokens": analysis.prompt_tokens,
        "completion_tokens": analysis.completion_tokens,
        "total_tokens": analysis.total_tokens,
        "cost": analysis.cost,
        "created_at": analysis.created_at,
        "updated_at": analysis.updated_at,
        "error_code": latest_job.error_code if latest_job else None,
        "started_at": latest_job.started_at if latest_job else None,
        "finished_at": latest_job.finished_at if latest_job else None,
        "progress_hint": latest_job.progress_hint if latest_job else None,
        "source_pages_count": latest_job.source_pages_count if latest_job else None,
        "job_id": latest_job.id if latest_job else None,
    }
