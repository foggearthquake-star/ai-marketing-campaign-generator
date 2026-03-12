"""API v1 job endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.job_run import JobRun
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership
from app.schemas.v1.job import JobResponse

router = APIRouter(prefix="/jobs", tags=["v1-jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> JobRun:
    """Return workspace job status for polling."""
    membership = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id, WorkspaceMembership.user_id == user.id)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Workspace access denied.")

    job = db.get(JobRun, job_id)
    if job is None or job.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
