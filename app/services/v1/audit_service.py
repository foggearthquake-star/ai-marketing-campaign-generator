"""Audit logging service."""

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    """Writes audit events."""

    @staticmethod
    def log(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: str,
        *,
        workspace_id: int | None = None,
        user_id: int | None = None,
        details: dict | None = None,
        legal_disclaimer: str | None = None,
    ) -> AuditLog:
        """Create and persist an audit log record."""
        record = AuditLog(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
            legal_disclaimer=legal_disclaimer,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
