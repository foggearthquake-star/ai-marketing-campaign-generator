"""Project schema definitions."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Input schema for creating a project."""

    name: str = Field(min_length=1, max_length=200)
    client_url: str = Field(min_length=1, max_length=500)


class ProjectResponse(BaseModel):
    """Output schema for project entity."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    client_url: str
    created_at: datetime
    updated_at: datetime


class ProjectAnalysisResponse(BaseModel):
    """Output schema for project website analysis."""

    project_id: int
    positioning: str
    target_audience: str
    strengths: str
    weaknesses: str
    campaign_angle: str
