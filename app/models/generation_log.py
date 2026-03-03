"""Generation log model placeholders."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class GenerationLog:
    """Minimal generation log entity for MVP scaffold."""

    id: int
    project_id: int
    input_data: str
    output_data: str
    token_usage: int
    status: str
    created_at: datetime
    updated_at: datetime
