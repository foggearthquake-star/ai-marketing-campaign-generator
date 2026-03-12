"""Authentication schemas for API v1."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Input payload for account registration."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8, max_length=128)
    workspace_name: str = Field(min_length=1, max_length=200)


class LoginRequest(BaseModel):
    """Input payload for account login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthTokenResponse(BaseModel):
    """Authentication response with bearer token."""

    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class UserProfileResponse(BaseModel):
    """Current user profile payload."""

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
