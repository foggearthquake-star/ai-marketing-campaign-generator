"""Workspace and membership schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class WorkspaceCreateRequest(BaseModel):
    """Workspace creation payload."""

    name: str = Field(min_length=1, max_length=200)


class WorkspaceResponse(BaseModel):
    """Workspace payload."""

    id: int
    name: str
    slug: str
    plan_tier: str
    plan_limits: dict
    created_at: datetime


class MembershipAddRequest(BaseModel):
    """Add member payload."""

    email: EmailStr
    role: str = Field(default="member")


class MembershipResponse(BaseModel):
    """Membership payload."""

    id: int
    workspace_id: int
    user_id: int
    role: str
    created_at: datetime
