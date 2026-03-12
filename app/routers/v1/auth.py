"""API v1 auth endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import JWT_EXPIRES_MINUTES
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.v1.auth import AuthTokenResponse, LoginRequest, RegisterRequest, UserProfileResponse
from app.services.v1.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["v1-auth"])


@router.post("/register", response_model=AuthTokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)) -> AuthTokenResponse:
    """Register user and workspace."""
    _, token = AuthService.register(
        db,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        workspace_name=payload.workspace_name,
    )
    return AuthTokenResponse(access_token=token, expires_in_seconds=JWT_EXPIRES_MINUTES * 60)


@router.post("/login", response_model=AuthTokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db_session)) -> AuthTokenResponse:
    """Authenticate user."""
    _, token = AuthService.login(db, email=payload.email, password=payload.password)
    return AuthTokenResponse(access_token=token, expires_in_seconds=JWT_EXPIRES_MINUTES * 60)


@router.get("/me", response_model=UserProfileResponse)
def me(user: User = Depends(get_current_user)) -> UserProfileResponse:
    """Return current user profile."""
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )
