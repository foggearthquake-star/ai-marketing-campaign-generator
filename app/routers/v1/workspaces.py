"""API v1 workspace endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from app.schemas.v1.workspace import (
    MembershipAddRequest,
    MembershipResponse,
    WorkspaceCreateRequest,
    WorkspaceResponse,
)
from app.services.v1.audit_service import AuditService
from app.services.v1.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["v1-workspaces"])


@router.get("/", response_model=list[WorkspaceResponse])
def list_workspaces(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[Workspace]:
    """List workspaces visible to current user."""
    return WorkspaceService.list_for_user(db, user.id)


@router.post("/", response_model=WorkspaceResponse)
def create_workspace(
    payload: WorkspaceCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Workspace:
    """Create workspace and attach current user as owner."""
    workspace = WorkspaceService.create_workspace(db, payload.name)
    WorkspaceService.add_member(db, workspace.id, user.id, "owner")
    AuditService.log(
        db,
        action="workspace.created",
        entity_type="workspace",
        entity_id=str(workspace.id),
        workspace_id=workspace.id,
        user_id=user.id,
        details={"name": workspace.name},
    )
    return workspace


@router.post("/{workspace_id}/members", response_model=MembershipResponse)
def add_member(
    workspace_id: int,
    payload: MembershipAddRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> WorkspaceMembership:
    """Add existing user to workspace with role."""
    membership = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id, WorkspaceMembership.user_id == user.id)
        .first()
    )
    if membership is None or membership.role != "owner":
        raise HTTPException(status_code=403, detail="Only workspace owners can add members.")

    member_user = WorkspaceService.find_user_by_email(db, payload.email)
    if member_user is None:
        raise HTTPException(status_code=404, detail="User with this email was not found.")

    created = WorkspaceService.add_member(db, workspace_id, member_user.id, payload.role)
    AuditService.log(
        db,
        action="workspace.member_added",
        entity_type="workspace",
        entity_id=str(workspace_id),
        workspace_id=workspace_id,
        user_id=user.id,
        details={"member_user_id": member_user.id, "role": created.role},
    )
    return created
