"""Workspace and membership service."""

import re

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership, WorkspaceRole


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "workspace"


class WorkspaceService:
    """Workspace domain service."""

    @staticmethod
    def create_workspace(db: Session, name: str) -> Workspace:
        """Create workspace with unique slug."""
        base_slug = _slugify(name)
        slug = base_slug
        idx = 1
        while db.query(Workspace).filter(Workspace.slug == slug).first() is not None:
            slug = f"{base_slug}-{idx}"
            idx += 1

        workspace = Workspace(name=name, slug=slug)
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def add_member(db: Session, workspace_id: int, user_id: int, role: str) -> WorkspaceMembership:
        """Add user membership into workspace."""
        existing = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.user_id == user_id,
            )
            .first()
        )
        if existing is not None:
            return existing

        normalized_role = role if role in {WorkspaceRole.owner.value, WorkspaceRole.member.value} else "member"
        membership = WorkspaceMembership(
            workspace_id=workspace_id,
            user_id=user_id,
            role=normalized_role,
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    @staticmethod
    def list_for_user(db: Session, user_id: int) -> list[Workspace]:
        """List workspaces where user is member."""
        return (
            db.query(Workspace)
            .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
            .filter(WorkspaceMembership.user_id == user_id)
            .order_by(Workspace.created_at.desc())
            .all()
        )

    @staticmethod
    def find_user_by_email(db: Session, email: str) -> User | None:
        """Find user by email."""
        return db.query(User).filter(User.email == email.lower().strip()).first()
