"""InsightMetric and GuidelineGap models for governance analytics and feedback loops."""

import uuid
from sqlalchemy import String, Text, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, TenantMixin


class InsightMetric(Base, TimestampMixin, TenantMixin):
    """Aggregated governance metric recorded over time."""

    __tablename__ = "insight_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "dispute_rate", "findings_by_category"
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    dimensions: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # {"channel": "social", "category": "tone"}


class GuidelineGap(Base, TimestampMixin, TenantMixin):
    """Candidate guideline gap surfaced by clustering overrides, disputes, and repeated issues."""

    __tablename__ = "guideline_gaps"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("guideline_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    override_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    dispute_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recurring_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    suggested_clarification: Mapped[str] = mapped_column(Text, nullable=False)
    example_cases: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    rule: Mapped["GuidelineRule"] = relationship("GuidelineRule", back_populates="gaps")
