"""Analytics service implementation."""

from sqlalchemy.orm import Session

from app.models.campaign import Campaign


class AnalyticsService:
    """Service for usage and cost analytics."""

    @staticmethod
    def get_usage_stats(db: Session) -> dict:
        """Return aggregated AI usage stats from campaigns."""
        campaigns = db.query(Campaign).all()

        total_tokens = 0
        total_cost = 0.0

        for campaign in campaigns:
            if campaign.total_tokens is not None:
                total_tokens += campaign.total_tokens
            if campaign.cost is not None:
                total_cost += campaign.cost

        return {
            "total_campaigns": len(campaigns),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
        }
