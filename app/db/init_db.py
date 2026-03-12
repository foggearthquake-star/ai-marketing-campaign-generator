"""Database initialization entrypoint."""

from app.db.base import Base
from app.db.session import engine
from app.models import analysis as analysis_model  # noqa: F401
from app.models import audit_log as audit_log_model  # noqa: F401
from app.models import campaign as campaign_model  # noqa: F401
from app.models import job_run as job_run_model  # noqa: F401
from app.models import project as project_model  # noqa: F401
from app.models import project_workspace as project_workspace_model  # noqa: F401
from app.models import usage_event as usage_event_model  # noqa: F401
from app.models import user as user_model  # noqa: F401
from app.models import workspace as workspace_model  # noqa: F401
from app.models import workspace_membership as workspace_membership_model  # noqa: F401


def init_db() -> None:
    """Create all configured database tables."""
    Base.metadata.create_all(bind=engine)
