"""Campaign schema definitions."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Email(BaseModel):
    """Email item in campaign sequence."""

    subject: str
    body: str


class CampaignOutput(BaseModel):
    """Structured campaign generation output."""

    campaign_angle: str
    ads: list[str]
    email_sequence: list[Email]
    landing_page_outline: list[str]
    evaluation: dict | None = None


class CampaignResponse(BaseModel):
    """Output schema for campaign entity."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_id: int
    version: int
    parent_campaign_id: int | None
    status: str
    output: CampaignOutput
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    cost: float | None
    created_at: datetime


class CampaignQueuedResponse(BaseModel):
    """Immediate response after scheduling background generation."""

    campaign_id: int
    status: str
