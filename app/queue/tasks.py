"""Celery tasks."""

from app.queue.celery_app import celery_app
from app.queue.job_runners import run_analysis_job, run_campaign_job


@celery_app.task(name="analysis.job", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def analysis_job(job_id: str, analysis_id: int) -> None:
    """Celery task for analysis generation."""
    run_analysis_job(job_id, analysis_id)


@celery_app.task(name="campaign.job", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def campaign_job(job_id: str, campaign_id: int) -> None:
    """Celery task for campaign generation."""
    run_campaign_job(job_id, campaign_id)
