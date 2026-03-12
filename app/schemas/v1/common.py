"""Common API v1 schema definitions."""

from datetime import datetime

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standardized error payload."""

    error_code: str
    error_message: str
    request_id: str | None = None


class StatusResponse(BaseModel):
    """Simple status payload."""

    status: str
    timestamp: datetime
