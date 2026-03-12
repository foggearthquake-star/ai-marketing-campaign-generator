"""Analysis schema definitions."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TargetAudience(BaseModel):
    """Target audience structured fields."""

    demographics: dict
    psychographics: dict


class AnalysisStructuredOutput(BaseModel):
    """Structured LLM analysis output schema."""

    positioning: str
    target_audience: TargetAudience
    strengths: list[str]
    weaknesses: list[str]
    campaign_angle: str


class AnalysisResponse(BaseModel):
    """Output schema for analysis details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    status: str
    structured_output: AnalysisStructuredOutput | None
    error_message: str | None
    model: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    cost: float | None
    created_at: datetime
    updated_at: datetime


class AnalysisListItemResponse(BaseModel):
    """Lightweight analysis schema for list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
