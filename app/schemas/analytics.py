"""Analytics schema definitions."""

from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    """Output schema for analytics endpoint."""

    total_requests: int
    total_tokens_used: int
    number_of_projects: int
    most_common_input_type: str
