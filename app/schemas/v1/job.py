"""Background job schemas."""

from datetime import datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    """Unified job payload."""

    id: str
    workspace_id: int
    requested_by_user_id: int
    job_type: str
    entity_id: int
    status: str
    progress_hint: int | None
    error_code: str | None
    error_message: str | None
    source_pages_count: int | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime
