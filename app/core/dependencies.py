"""Dependency provider placeholders."""


def get_request_id() -> str:
    """Placeholder dependency to provide request correlation id."""
    return "mvp-request-id"
