"""Authentication service."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import JWT_EXPIRES_MINUTES, create_access_token, hash_password, verify_password
from app.models.user import User
from app.services.v1.audit_service import AuditService
from app.services.v1.workspace_service import WorkspaceService


class AuthService:
    """Handles registration and login."""

    @staticmethod
    def register(
        db: Session,
        email: str,
        full_name: str,
        password: str,
        workspace_name: str,
    ) -> tuple[User, str]:
        """Register a user, create workspace and return auth token."""
        normalized_email = email.lower().strip()
        existing = db.query(User).filter(User.email == normalized_email).first()
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

        user = User(
            email=normalized_email,
            full_name=full_name.strip(),
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        workspace = WorkspaceService.create_workspace(db, workspace_name)
        WorkspaceService.add_member(db, workspace.id, user.id, "owner")
        AuditService.log(
            db,
            action="user.registered",
            entity_type="user",
            entity_id=str(user.id),
            workspace_id=workspace.id,
            user_id=user.id,
            details={"email": user.email},
        )
        token = create_access_token(str(user.id), expires_minutes=JWT_EXPIRES_MINUTES)
        return user, token

    @staticmethod
    def login(db: Session, email: str, password: str) -> tuple[User, str]:
        """Authenticate and return JWT token."""
        normalized_email = email.lower().strip()
        user = db.query(User).filter(User.email == normalized_email).first()
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive.")
        token = create_access_token(str(user.id), expires_minutes=JWT_EXPIRES_MINUTES)
        return user, token
