"""Campaign schemas for API v1."""

from datetime import datetime

from pydantic import BaseModel


class CampaignQueuedResponse(BaseModel):
    """Response when campaign generation has been queued."""

    campaign_id: int
    job_id: str
    status: str


class CampaignResponse(BaseModel):
    """Campaign payload in API v1."""

    id: int
    analysis_id: int
    version: int
    parent_campaign_id: int | None
    status: str
    output: dict
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    cost: float | None
    created_at: datetime
