"""Time utility helpers."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc)
