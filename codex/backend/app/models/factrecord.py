"""FactRecord and TerminologyEntry models for claims and brand language governance."""

import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base, TimestampMixin, TenantMixin


class FactRecord(Base, TimestampMixin, TenantMixin):
    """Approved-facts register entry with ownership and expiry tracking."""

    __tablename__ = "fact_records"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brand_workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    statistic: Mapped[str] = mapped_column(String(255), nullable=False)   # e.g., "Market share", "#1 skincare brand"
    value: Mapped[str] = mapped_column(String(255), nullable=False)       # e.g., "Top 5 in category, 2025 survey"
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)        # department or person
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Embedding for claim similarity matching
    embedding: Mapped[Any | None] = mapped_column(Vector(1536), nullable=True)

    # Relationships
    workspace: Mapped["BrandWorkspace"] = relationship("BrandWorkspace", back_populates="fact_records")


class TerminologyEntry(Base, TimestampMixin, TenantMixin):
    """Brand vocabulary with preferred/banned status and contextual examples."""

    __tablename__ = "terminology_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brand_workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    term: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # preferred, banned
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # legal, tone, product
    preferred_alternative: Mapped[str | None] = mapped_column(String(100), nullable=True)
    examples: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    workspace: Mapped["BrandWorkspace"] = relationship("BrandWorkspace", back_populates="terminology_entries")
