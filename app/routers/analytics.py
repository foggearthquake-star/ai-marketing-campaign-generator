"""Analytics endpoints."""

from fastapi import APIRouter

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
