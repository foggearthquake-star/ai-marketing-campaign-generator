"""API v1 campaign endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.analysis import Analysis
from app.models.campaign import Campaign
from app.models.project_workspace import ProjectWorkspace
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership
from app.queue.dispatcher import dispatch_campaign
from app.schemas.v1.campaign import CampaignQueuedResponse, CampaignResponse
from app.services.campaign_compare import CampaignCompareService
from app.services.campaign_service import CampaignService
from app.services.v1.audit_service import AuditService
from app.services.v1.job_service import JobService

router = APIRouter(prefix="/campaigns", tags=["v1-campaigns"])


def _require_membership(db: Session, workspace_id: int, user_id: int) -> WorkspaceMembership:
    membership = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id, WorkspaceMembership.user_id == user_id)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Workspace access denied.")
    return membership


def _ensure_analysis_workspace(db: Session, analysis_id: int, workspace_id: int) -> Analysis:
    analysis = (
        db.query(Analysis)
        .join(ProjectWorkspace, ProjectWorkspace.project_id == Analysis.project_id)
        .filter(Analysis.id == analysis_id, ProjectWorkspace.workspace_id == workspace_id)
        .first()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found in workspace.")
    return analysis


@router.post("/{analysis_id}", response_model=CampaignQueuedResponse)
def generate_campaign(
    analysis_id: int,
    workspace_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> CampaignQueuedResponse:
    """Queue campaign generation and return job metadata."""
    _require_membership(db, workspace_id, user.id)
    _ensure_analysis_workspace(db, analysis_id, workspace_id)
    try:
        campaign = CampaignService.create_campaign_record(db, analysis_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    job = JobService.create(
        db,
        workspace_id=workspace_id,
        requested_by_user_id=user.id,
        job_type="campaign",
        entity_id=campaign.id,
    )
    dispatch_campaign(background_tasks, job.id, campaign.id)
    AuditService.log(
        db,
        action="campaign.queued",
        entity_type="campaign",
        entity_id=str(campaign.id),
        workspace_id=workspace_id,
        user_id=user.id,
        details={"job_id": job.id, "analysis_id": analysis_id},
    )
    return CampaignQueuedResponse(campaign_id=campaign.id, job_id=job.id, status=job.status)


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Campaign:
    """Return workspace campaign."""
    _require_membership(db, workspace_id, user.id)
    campaign = (
        db.query(Campaign)
        .join(Analysis, Analysis.id == Campaign.analysis_id)
        .join(ProjectWorkspace, ProjectWorkspace.project_id == Analysis.project_id)
        .filter(Campaign.id == campaign_id, ProjectWorkspace.workspace_id == workspace_id)
        .first()
    )
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign


@router.get("/{campaign_id}/compare/{other_campaign_id}")
def compare_campaigns(
    campaign_id: int,
    other_campaign_id: int,
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> dict:
    """Compare two campaigns in same workspace."""
    _require_membership(db, workspace_id, user.id)
    campaign_a = (
        db.query(Campaign)
        .join(Analysis, Analysis.id == Campaign.analysis_id)
        .join(ProjectWorkspace, ProjectWorkspace.project_id == Analysis.project_id)
        .filter(Campaign.id == campaign_id, ProjectWorkspace.workspace_id == workspace_id)
        .first()
    )
    campaign_b = (
        db.query(Campaign)
        .join(Analysis, Analysis.id == Campaign.analysis_id)
        .join(ProjectWorkspace, ProjectWorkspace.project_id == Analysis.project_id)
        .filter(Campaign.id == other_campaign_id, ProjectWorkspace.workspace_id == workspace_id)
        .first()
    )
    if campaign_a is None or campaign_b is None:
        raise HTTPException(status_code=404, detail="One or both campaigns not found.")
    return CampaignCompareService.compare_campaigns(campaign_a, campaign_b)
