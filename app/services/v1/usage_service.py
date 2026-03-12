"""Usage and limits service."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.project_workspace import ProjectWorkspace
from app.models.usage_event import UsageEvent
from app.models.workspace import Workspace


class UsageService:
    """Computes usage and limits per workspace."""

    @staticmethod
    def track(db: Session, workspace_id: int, event_type: str, quantity: int = 1, metadata: dict | None = None) -> None:
        """Persist a usage event."""
        event = UsageEvent(
            workspace_id=workspace_id,
            event_type=event_type,
            quantity=quantity,
            metadata_json=metadata or {},
        )
        db.add(event)
        db.commit()

    @staticmethod
    def usage_summary(db: Session, workspace_id: int) -> dict:
        """Return aggregated workspace usage."""
        events = db.query(UsageEvent).filter(UsageEvent.workspace_id == workspace_id).all()
        total_analyses = sum(e.quantity for e in events if e.event_type == "analysis.created")
        total_campaigns = sum(e.quantity for e in events if e.event_type == "campaign.created")
        total_tokens = sum(
            UsageService._to_int((e.metadata_json or {}).get("total_tokens"))
            for e in events
            if e.event_type == "campaign.created"
        )
        total_cost = float(
            sum(
                UsageService._to_float((e.metadata_json or {}).get("cost"))
                for e in events
                if e.event_type == "campaign.created"
            )
        )
        return {
            "workspace_id": workspace_id,
            "total_analyses": total_analyses,
            "total_campaigns": total_campaigns,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
        }

    @staticmethod
    def plan_info(db: Session, workspace_id: int) -> dict:
        """Return workspace plan details."""
        workspace = db.get(Workspace, workspace_id)
        if workspace is None:
            raise ValueError("Workspace not found.")
        return {
            "workspace_id": workspace.id,
            "plan_tier": workspace.plan_tier,
            "plan_limits": workspace.plan_limits,
        }

    @staticmethod
    def limits_info(db: Session, workspace_id: int) -> dict:
        """Compute limit usage and remaining."""
        plan = UsageService.plan_info(db, workspace_id)
        usage = UsageService.usage_summary(db, workspace_id)
        limits = plan["plan_limits"]
        period = datetime.now(timezone.utc).strftime("%Y-%m")
        remaining = {
            "projects": max(0, int(limits.get("projects", 0)) - UsageService._count_projects(db, workspace_id)),
            "analyses_per_month": max(
                0,
                int(limits.get("analyses_per_month", 0)) - int(usage["total_analyses"]),
            ),
            "campaigns_per_month": max(
                0,
                int(limits.get("campaigns_per_month", 0)) - int(usage["total_campaigns"]),
            ),
            "users": max(0, int(limits.get("users", 0)) - UsageService._count_users(db, workspace_id)),
        }
        return {
            "workspace_id": workspace_id,
            "limits": limits,
            "usage": {
                "projects": UsageService._count_projects(db, workspace_id),
                "analyses_per_month": usage["total_analyses"],
                "campaigns_per_month": usage["total_campaigns"],
                "users": UsageService._count_users(db, workspace_id),
                "period": period,
            },
            "remaining": remaining,
        }

    @staticmethod
    def _count_projects(db: Session, workspace_id: int) -> int:
        return db.query(ProjectWorkspace).filter(ProjectWorkspace.workspace_id == workspace_id).count()

    @staticmethod
    def _count_users(db: Session, workspace_id: int) -> int:
        from app.models.workspace_membership import WorkspaceMembership

        return db.query(WorkspaceMembership).filter(WorkspaceMembership.workspace_id == workspace_id).count()

    @staticmethod
    def _to_int(value: object) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _to_float(value: object) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0
