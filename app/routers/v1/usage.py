"""API v1 usage and plan endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership
from app.schemas.v1.usage import LimitsResponse, PlanResponse, UsageResponse
from app.services.v1.usage_service import UsageService

router = APIRouter(prefix="", tags=["v1-usage"])


def _require_membership(db: Session, workspace_id: int, user_id: int) -> None:
    membership = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id, WorkspaceMembership.user_id == user_id)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Workspace access denied.")


@router.get("/usage", response_model=UsageResponse)
def usage(
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> dict:
    """Return usage summary."""
    _require_membership(db, workspace_id, user.id)
    return UsageService.usage_summary(db, workspace_id)


@router.get("/plan", response_model=PlanResponse)
def plan(
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> dict:
    """Return workspace plan info."""
    _require_membership(db, workspace_id, user.id)
    return UsageService.plan_info(db, workspace_id)


@router.get("/limits", response_model=LimitsResponse)
def limits(
    workspace_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> dict:
    """Return current limits and remaining quotas."""
    _require_membership(db, workspace_id, user.id)
    return UsageService.limits_info(db, workspace_id)
