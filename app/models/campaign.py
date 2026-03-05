"""Campaign ORM model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CampaignStatus(str, Enum):
    """Campaign generation lifecycle status."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Campaign(Base):
    """Persisted generated marketing campaign."""

    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_campaign_id: Mapped[int | None] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=True,
    )
    status: Mapped[CampaignStatus] = mapped_column(
        String(20),
        default=CampaignStatus.pending,
    )
    output: Mapped[dict] = mapped_column(JSON)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
