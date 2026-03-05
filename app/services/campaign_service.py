"""Campaign generation service."""

from sqlalchemy.orm import Session

from app.ai.orchestrator import MarketingOrchestrator
from app.db.session import SessionLocal
from app.models.analysis import Analysis
from app.models.campaign import Campaign, CampaignStatus


class CampaignService:
    """Service for campaign persistence and background execution."""

    @staticmethod
    def create_campaign_record(
        db: Session,
        analysis_id: int,
        parent_campaign_id: int | None = None,
    ) -> Campaign:
        """Create a pending campaign placeholder record."""
        analysis = db.get(Analysis, analysis_id)
        if analysis is None:
            raise ValueError("Analysis not found.")
        if not analysis.structured_output:
            raise ValueError("Analysis has no structured output.")

        next_version = CampaignService._get_next_version(db, analysis_id)
        campaign = Campaign(
            analysis_id=analysis_id,
            version=next_version,
            parent_campaign_id=parent_campaign_id,
            status=CampaignStatus.pending,
            output={
                "campaign_angle": "",
                "ads": [],
                "email_sequence": [],
                "landing_page_outline": [],
            },
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            cost=None,
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    def run_campaign_generation(campaign_id: int) -> None:
        """Generate campaign output in background and persist it."""
        db = SessionLocal()
        try:
            campaign = db.get(Campaign, campaign_id)
            if campaign is None:
                return

            campaign.status = CampaignStatus.running
            db.commit()

            try:
                analysis = db.get(Analysis, campaign.analysis_id)
                if analysis is None or not analysis.structured_output:
                    raise ValueError("Analysis not ready for campaign generation.")

                output, usage = MarketingOrchestrator.build_campaign_output_with_usage(
                    analysis.structured_output
                )
                campaign.output = output
                campaign.prompt_tokens = usage.get("prompt_tokens")
                campaign.completion_tokens = usage.get("completion_tokens")
                campaign.total_tokens = usage.get("total_tokens")
                campaign.cost = CampaignService._calculate_cost(campaign.total_tokens)
                campaign.status = CampaignStatus.completed
                db.commit()
                db.refresh(campaign)
            except Exception:
                campaign.status = CampaignStatus.failed
                db.commit()
        finally:
            db.close()

    @staticmethod
    def generate_campaign(db: Session, analysis_id: int) -> Campaign:
        """Generate and persist a campaign synchronously."""
        analysis = db.get(Analysis, analysis_id)
        if analysis is None:
            raise ValueError("Analysis not found.")
        if not analysis.structured_output:
            raise ValueError("Analysis has no structured output.")

        result, usage = MarketingOrchestrator.build_campaign_output_with_usage(
            analysis.structured_output
        )
        next_version = CampaignService._get_next_version(db, analysis_id)
        campaign = Campaign(
            analysis_id=analysis_id,
            version=next_version,
            parent_campaign_id=None,
            status=CampaignStatus.completed,
            output=result,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            cost=CampaignService._calculate_cost(usage.get("total_tokens")),
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    def list_campaigns_by_analysis_id(db: Session, analysis_id: int) -> list[Campaign]:
        """Return campaigns for analysis ordered by newest first."""
        return (
            db.query(Campaign)
            .filter(Campaign.analysis_id == analysis_id)
            .order_by(Campaign.created_at.desc())
            .all()
        )

    @staticmethod
    def _get_next_version(db: Session, analysis_id: int) -> int:
        """Calculate next campaign version for an analysis."""
        latest = (
            db.query(Campaign)
            .filter(Campaign.analysis_id == analysis_id)
            .order_by(Campaign.version.desc())
            .first()
        )
        if latest is None:
            return 1
        return int(latest.version) + 1

    @staticmethod
    def _calculate_cost(total_tokens: int | None) -> float | None:
        """Estimate simple token cost."""
        if total_tokens is None:
            return None
        return (total_tokens / 1000) * 0.002
