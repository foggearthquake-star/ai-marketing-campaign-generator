"""Campaign endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.analysis import Analysis
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignQueuedResponse, CampaignResponse
from app.services.campaign_compare import CampaignCompareService
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
history_router = APIRouter(prefix="/analyses", tags=["campaigns"])


@router.post("/{analysis_id}", response_model=CampaignQueuedResponse)
def generate_campaign(
    analysis_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
) -> CampaignQueuedResponse:
    """Create campaign record and schedule background generation."""
    try:
        campaign = CampaignService.create_campaign_record(db, analysis_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    background_tasks.add_task(
        CampaignService.run_campaign_generation,
        campaign.id,
    )
    return CampaignQueuedResponse(
        campaign_id=campaign.id,
        status="pending",
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: int, db: Session = Depends(get_db_session)) -> CampaignResponse:
    """Return campaign by ID for polling."""
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign


@router.get("/{campaign_id}/compare/{other_campaign_id}")
def compare_campaigns(
    campaign_id: int,
    other_campaign_id: int,
    db: Session = Depends(get_db_session),
) -> dict:
    """Compare two campaigns and return key differences."""
    campaign_a = db.get(Campaign, campaign_id)
    if campaign_a is None:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    campaign_b = db.get(Campaign, other_campaign_id)
    if campaign_b is None:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    return CampaignCompareService.compare_campaigns(campaign_a, campaign_b)


@history_router.get("/{analysis_id}/campaigns", response_model=list[CampaignResponse])
def list_analysis_campaigns(analysis_id: int, db: Session = Depends(get_db_session)) -> list[CampaignResponse]:
    """Return campaign history for an analysis."""
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return CampaignService.list_campaigns_by_analysis_id(db, analysis_id)
