"""Background runner functions with job tracking."""

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.analysis import Analysis
from app.models.campaign import Campaign
from app.models.job_run import JobRun
from app.services.analysis_service import AnalysisService
from app.services.campaign_service import CampaignService
from app.services.v1.audit_service import AuditService
from app.services.v1.job_service import JobService
from app.services.v1.usage_service import UsageService


def run_analysis_job(job_id: str, analysis_id: int) -> None:
    """Run analysis and update unified job status."""
    db: Session = SessionLocal()
    try:
        job = db.get(JobRun, job_id)
        if job is None:
            return
        JobService.mark_running(db, job, progress_hint=35)
        AnalysisService.run_analysis(analysis_id)
        analysis = db.get(Analysis, analysis_id)
        if analysis is None:
            JobService.mark_failed(db, job, "analysis_not_found", "Analysis record disappeared.")
            return
        if analysis.status == "failed":
            JobService.mark_failed(db, job, "analysis_failed", analysis.error_message or "Analysis failed.")
            return
        JobService.mark_completed(db, job, progress_hint=100, source_pages_count=1)
        UsageService.track(
            db,
            job.workspace_id,
            "analysis.created",
            metadata={"analysis_id": analysis_id},
        )
        AuditService.log(
            db,
            action="analysis.completed",
            entity_type="analysis",
            entity_id=str(analysis_id),
            workspace_id=job.workspace_id,
            user_id=job.requested_by_user_id,
            details={"job_id": job.id, "status": analysis.status},
            legal_disclaimer="Aggressive website fetch mode enabled by workspace policy.",
        )
    except Exception as exc:
        job = db.get(JobRun, job_id)
        if job is not None:
            JobService.mark_failed(db, job, "analysis_exception", str(exc))
    finally:
        db.close()


def run_campaign_job(job_id: str, campaign_id: int) -> None:
    """Run campaign generation and update unified job status."""
    db: Session = SessionLocal()
    try:
        job = db.get(JobRun, job_id)
        if job is None:
            return
        JobService.mark_running(db, job, progress_hint=45)
        CampaignService.run_campaign_generation(campaign_id)
        campaign = db.get(Campaign, campaign_id)
        if campaign is None:
            JobService.mark_failed(db, job, "campaign_not_found", "Campaign record disappeared.")
            return
        if campaign.status == "failed":
            JobService.mark_failed(db, job, "campaign_failed", "Campaign generation failed.")
            return
        JobService.mark_completed(db, job, progress_hint=100)
        UsageService.track(
            db,
            job.workspace_id,
            "campaign.created",
            metadata={"campaign_id": campaign_id, "total_tokens": campaign.total_tokens, "cost": campaign.cost},
        )
        AuditService.log(
            db,
            action="campaign.completed",
            entity_type="campaign",
            entity_id=str(campaign_id),
            workspace_id=job.workspace_id,
            user_id=job.requested_by_user_id,
            details={"job_id": job.id, "status": campaign.status},
        )
    except Exception as exc:
        job = db.get(JobRun, job_id)
        if job is not None:
            JobService.mark_failed(db, job, "campaign_exception", str(exc))
    finally:
        db.close()
