"""Shared schema definitions."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Simple message response schema."""

    message: str
