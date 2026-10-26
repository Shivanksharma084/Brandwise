"""GuidelineDocument and GuidelineRule models with vector embeddings and atomic rules."""

import uuid
from typing import Any
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base, TimestampMixin, TenantMixin


class GuidelineDocument(Base, TimestampMixin, TenantMixin):
    """Uploaded guideline document (PDF/DOCX/MD) parsed into rules."""

    __tablename__ = "guideline_documents"

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
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # pdf, docx, md
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    workspace: Mapped["BrandWorkspace"] = relationship("BrandWorkspace", back_populates="guideline_documents")
    rules: Mapped[list["GuidelineRule"]] = relationship("GuidelineRule", back_populates="document", cascade="all, delete-orphan")


class GuidelineRule(Base, TimestampMixin, TenantMixin):
    """Atomic, citable brand guideline rule extracted from a guideline document."""

    __tablename__ = "guideline_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("guideline_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clause_ref: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "§2.1", "Clause 4.3"
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)   # tone, terminology, messaging, disclaimer, visual, accessibility
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # high, medium, low, advisory
    channels: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)      # ["social", "web", "email", "print"]
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    original_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # pgvector embedding for retrieval-grounded checks (1536 dim for OpenAI, configurable)
    embedding: Mapped[Any | None] = mapped_column(Vector(1536), nullable=True)

    # Relationships
    document: Mapped["GuidelineDocument"] = relationship("GuidelineDocument", back_populates="rules")
    findings: Mapped[list["ReviewFinding"]] = relationship("ReviewFinding", back_populates="rule")
    gaps: Mapped[list["GuidelineGap"]] = relationship("GuidelineGap", back_populates="rule")
