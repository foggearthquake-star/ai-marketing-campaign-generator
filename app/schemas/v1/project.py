"""Project schemas for API v1."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    """Create project payload."""

    workspace_id: int
    name: str = Field(min_length=1, max_length=200)
    client_url: str = Field(min_length=1, max_length=500)


class ProjectResponse(BaseModel):
    """Project payload."""

    id: int
    workspace_id: int
    name: str
    client_url: str
    created_at: datetime
    updated_at: datetime


class AnalyzeResponse(BaseModel):
    """Response after analysis has been queued."""

    analysis_id: int
    job_id: str
    status: str


class ProjectAnalysisListItem(BaseModel):
    """Lightweight analysis item for project history in workspace."""

    id: int
    project_id: int
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
