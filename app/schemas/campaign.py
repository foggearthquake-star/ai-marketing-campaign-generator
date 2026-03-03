"""Campaign schema definitions."""

from pydantic import BaseModel


class CampaignRequest(BaseModel):
    """Input schema for campaign generation."""

    brief: str


class CampaignResponse(BaseModel):
    """Output schema for campaign generation."""

    result: str
