"""Job management service."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.job_run import JobRun, JobStatus


class JobService:
    """Create/update background job records."""

    @staticmethod
    def create(
        db: Session,
        workspace_id: int,
        requested_by_user_id: int,
        job_type: str,
        entity_id: int,
    ) -> JobRun:
        """Create queued job."""
        job = JobRun(
            workspace_id=workspace_id,
            requested_by_user_id=requested_by_user_id,
            job_type=job_type,
            entity_id=entity_id,
            status=JobStatus.queued.value,
            progress_hint=5,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def mark_running(db: Session, job: JobRun, progress_hint: int = 30) -> JobRun:
        """Move job to running."""
        job.status = JobStatus.running.value
        job.started_at = datetime.now(timezone.utc)
        job.progress_hint = progress_hint
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def mark_completed(
        db: Session,
        job: JobRun,
        *,
        progress_hint: int = 100,
        source_pages_count: int | None = None,
    ) -> JobRun:
        """Move job to completed."""
        job.status = JobStatus.completed.value
        job.finished_at = datetime.now(timezone.utc)
        job.progress_hint = progress_hint
        if source_pages_count is not None:
            job.source_pages_count = source_pages_count
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def mark_failed(db: Session, job: JobRun, error_code: str, error_message: str) -> JobRun:
        """Move job to failed."""
        job.status = JobStatus.failed.value
        job.finished_at = datetime.now(timezone.utc)
        job.progress_hint = 100
        job.error_code = error_code
        job.error_message = error_message[:2000]
        db.commit()
        db.refresh(job)
        return job
