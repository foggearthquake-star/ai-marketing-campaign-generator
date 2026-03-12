"""API v1 project endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.analysis import Analysis
from app.models.project_workspace import ProjectWorkspace
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership
from app.queue.dispatcher import dispatch_analysis
from app.schemas.v1.project import AnalyzeResponse, ProjectAnalysisListItem, ProjectCreateRequest, ProjectResponse
from app.services.analysis_service import AnalysisService
from app.services.v1.audit_service import AuditService
from app.services.v1.job_service import JobService
from app.services.v1.project_service import ProjectV1Service

router = APIRouter(prefix="/projects", tags=["v1-projects"])


def _require_membership(db: Session, workspace_id: int, user_id: int) -> WorkspaceMembership:
    membership = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id, WorkspaceMembership.user_id == user_id)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Workspace access denied.")
    return membership


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[ProjectResponse]:
    """List workspace projects."""
    _require_membership(db, workspace_id, user.id)
    projects = ProjectV1Service.list_projects(db, workspace_id)
    return [
        ProjectResponse(
            id=p.id,
            workspace_id=workspace_id,
            name=p.name,
            client_url=p.client_url,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]


@router.post("/", response_model=ProjectResponse)
def create_project(
    payload: ProjectCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ProjectResponse:
    """Create workspace project."""
    _require_membership(db, payload.workspace_id, user.id)
    project, _ = ProjectV1Service.create_project(
        db,
        workspace_id=payload.workspace_id,
        created_by_user_id=user.id,
        name=payload.name,
        client_url=payload.client_url,
    )
    AuditService.log(
        db,
        action="project.created",
        entity_type="project",
        entity_id=str(project.id),
        workspace_id=payload.workspace_id,
        user_id=user.id,
        details={"name": project.name, "client_url": project.client_url},
    )
    return ProjectResponse(
        id=project.id,
        workspace_id=payload.workspace_id,
        name=project.name,
        client_url=project.client_url,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("/{project_id}/analyze", response_model=AnalyzeResponse)
def analyze_project(
    project_id: int,
    workspace_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AnalyzeResponse:
    """Create analysis record and queue job."""
    _require_membership(db, workspace_id, user.id)
    try:
        project = ProjectV1Service.ensure_workspace_project(db, workspace_id, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not project.client_url:
        raise HTTPException(status_code=400, detail="Project client_url is missing.")

    analysis = AnalysisService.create_analysis(db, project.id)
    job = JobService.create(
        db,
        workspace_id=workspace_id,
        requested_by_user_id=user.id,
        job_type="analysis",
        entity_id=analysis.id,
    )
    dispatch_analysis(background_tasks, job.id, analysis.id)
    AuditService.log(
        db,
        action="analysis.queued",
        entity_type="analysis",
        entity_id=str(analysis.id),
        workspace_id=workspace_id,
        user_id=user.id,
        details={"job_id": job.id},
        legal_disclaimer="Aggressive website fetch mode enabled by workspace policy.",
    )
    return AnalyzeResponse(analysis_id=analysis.id, job_id=job.id, status=job.status)


@router.get("/{project_id}/analyses", response_model=list[ProjectAnalysisListItem])
def list_project_analyses(
    project_id: int,
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[ProjectAnalysisListItem]:
    """List analyses for project within workspace."""
    _require_membership(db, workspace_id, user.id)
    ProjectV1Service.ensure_workspace_project(db, workspace_id, project_id)

    analyses = (
        db.query(Analysis)
        .join(ProjectWorkspace, ProjectWorkspace.project_id == Analysis.project_id)
        .filter(Analysis.project_id == project_id, ProjectWorkspace.workspace_id == workspace_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    return [
        ProjectAnalysisListItem(
            id=item.id,
            project_id=item.project_id,
            status=item.status,
            error_message=item.error_message,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in analyses
    ]
