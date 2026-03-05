"""Campaign comparison utilities."""

from app.models.campaign import Campaign


class CampaignCompareService:
    """Service for comparing two campaign versions."""

    @staticmethod
    def compare_campaigns(campaign_a: Campaign, campaign_b: Campaign) -> dict:
        output_a = campaign_a.output or {}
        output_b = campaign_b.output or {}

        angle_a = str(output_a.get("campaign_angle", ""))
        angle_b = str(output_b.get("campaign_angle", ""))

        ads_a = output_a.get("ads")
        ads_b = output_b.get("ads")
        ads_count_a = len(ads_a) if isinstance(ads_a, list) else 0
        ads_count_b = len(ads_b) if isinstance(ads_b, list) else 0

        emails_a = output_a.get("email_sequence")
        emails_b = output_b.get("email_sequence")
        email_count_a = len(emails_a) if isinstance(emails_a, list) else 0
        email_count_b = len(emails_b) if isinstance(emails_b, list) else 0

        landing_a = output_a.get("landing_page_outline")
        landing_b = output_b.get("landing_page_outline")
        landing_count_a = len(landing_a) if isinstance(landing_a, list) else 0
        landing_count_b = len(landing_b) if isinstance(landing_b, list) else 0

        return {
            "campaign_a": output_a,
            "campaign_b": output_b,
            "differences": {
                "angle_changed": angle_a != angle_b,
                "ads_count_diff": ads_count_b - ads_count_a,
                "email_diff": email_count_a != email_count_b,
                "landing_diff": landing_count_a != landing_count_b,
            },
        }
