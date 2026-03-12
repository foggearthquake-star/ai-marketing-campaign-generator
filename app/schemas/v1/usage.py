"""Usage and limits schemas."""

from pydantic import BaseModel


class UsageResponse(BaseModel):
    """Aggregated usage payload."""

    workspace_id: int
    total_analyses: int
    total_campaigns: int
    total_tokens: int
    total_cost: float


class PlanResponse(BaseModel):
    """Workspace plan payload."""

    workspace_id: int
    plan_tier: str
    plan_limits: dict


class LimitsResponse(BaseModel):
    """Current limits and consumption payload."""

    workspace_id: int
    limits: dict
    usage: dict
    remaining: dict
