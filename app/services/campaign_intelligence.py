"""Campaign intelligence utilities."""

from typing import List

from sqlalchemy.orm import Session

from app.models.campaign import Campaign


class CampaignIntelligence:
    """Utility layer for historical campaign insights."""

    @staticmethod
    def extract_angles(campaigns: List[Campaign]) -> list[str]:
        angles = []

        for campaign in campaigns:
            output = campaign.output or {}
            angle = output.get("campaign_angle")
            if isinstance(angle, str):
                angles.append(angle)

        return angles

    @staticmethod
    def extract_ads(campaigns: List[Campaign]) -> list[str]:
        ads = []

        for campaign in campaigns:
            output = campaign.output or {}
            campaign_ads = output.get("ads")
            if isinstance(campaign_ads, list):
                ads.extend(campaign_ads)

        return ads

    @staticmethod
    def summarize_history(campaigns: List[Campaign]) -> dict:
        angles = CampaignIntelligence.extract_angles(campaigns)
        ads = CampaignIntelligence.extract_ads(campaigns)

        return {
            "previous_campaigns": len(campaigns),
            "angles": angles,
            "ads": ads,
        }

    @staticmethod
    def get_campaign_history(db: Session, analysis_id: int) -> list[Campaign]:
        return (
            db.query(Campaign)
            .filter(Campaign.analysis_id == analysis_id)
            .order_by(Campaign.created_at.desc())
            .limit(5)
            .all()
        )

    @staticmethod
    def build_learning_context(campaigns: list[Campaign]) -> dict:
        summary = CampaignIntelligence.summarize_history(campaigns)

        return {
            "previous_campaign_count": summary["previous_campaigns"],
            "previous_angles": summary["angles"],
            "previous_ads": summary["ads"],
        }
