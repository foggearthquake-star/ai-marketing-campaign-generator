"""Dispatch async jobs to Celery or local fallback."""

import os

from fastapi import BackgroundTasks
from kombu.exceptions import OperationalError

from app.queue.celery_app import celery_app
from app.queue.job_runners import run_analysis_job, run_campaign_job

CELERY_ENABLED = bool(os.getenv("CELERY_BROKER_URL"))
RUN_TASKS_LOCALLY = os.getenv("RUN_TASKS_LOCALLY", "1") == "1"


def dispatch_analysis(background_tasks: BackgroundTasks, job_id: str, analysis_id: int) -> None:
    """Queue analysis task with Celery fallback."""
    if CELERY_ENABLED and not RUN_TASKS_LOCALLY:
        try:
            celery_app.send_task("analysis.job", args=[job_id, analysis_id])
            return
        except OperationalError:
            # Broker is unavailable in local/dev: fall back to in-process task.
            pass
    background_tasks.add_task(run_analysis_job, job_id, analysis_id)


def dispatch_campaign(background_tasks: BackgroundTasks, job_id: str, campaign_id: int) -> None:
    """Queue campaign task with Celery fallback."""
    if CELERY_ENABLED and not RUN_TASKS_LOCALLY:
        try:
            celery_app.send_task("campaign.job", args=[job_id, campaign_id])
            return
        except OperationalError:
            # Broker is unavailable in local/dev: fall back to in-process task.
            pass
    background_tasks.add_task(run_campaign_job, job_id, campaign_id)
