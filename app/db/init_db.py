"""Database initialization entrypoint."""

from app.db.base import Base
from app.db.session import engine
from app.models import analysis as analysis_model  # noqa: F401
from app.models import campaign as campaign_model  # noqa: F401
from app.models import project as project_model  # noqa: F401


def init_db() -> None:
    """Create all configured database tables."""
    Base.metadata.create_all(bind=engine)
