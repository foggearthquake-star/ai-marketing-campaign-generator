"""Analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/")
def analytics_overview() -> dict[str, int | str]:
    """Return placeholder analytics for MVP scaffold."""
    return {
        "total_requests": 0,
        "total_tokens_used": 0,
        "number_of_projects": 0,
        "most_common_input_type": "n/a",
    }


@router.get("/usage")
def analytics_usage(db: Session = Depends(get_db_session)) -> dict:
    """Return AI usage and cost metrics."""
    return AnalyticsService.get_usage_stats(db)
