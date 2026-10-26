"""ContentSubmission and ReviewFinding models."""

import uuid
from sqlalchemy import String, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, TenantMixin


class ContentSubmission(Base, TimestampMixin, TenantMixin):
    """Submitted content draft (text, social post, document, image) for review."""

    __tablename__ = "content_submissions"

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
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # text, image, pdf, docx
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True)     # social, blog, email, ad
    campaign: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_ai_assisted: Mapped[bool] = mapped_column(default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)  # draft, in_review, changes_requested, approved, exported
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Relationships
    workspace: Mapped["BrandWorkspace"] = relationship("BrandWorkspace", back_populates="submissions")
    creator: Mapped["User"] = relationship("User", back_populates="submissions")
    findings: Mapped[list["ReviewFinding"]] = relationship("ReviewFinding", back_populates="submission", cascade="all, delete-orphan")
    workflow_states: Mapped[list["WorkflowState"]] = relationship("WorkflowState", back_populates="submission", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="submission", cascade="all, delete-orphan")


class ReviewFinding(Base, TimestampMixin, TenantMixin):
    """Individual brand compliance flag with source citation and suggested fix."""

    __tablename__ = "review_findings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("content_submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("guideline_rules.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)    # tone, claim, terminology, visual, accessibility, disclaimer
    severity: Mapped[str] = mapped_column(String(20), nullable=False)    # high, medium, low, advisory
    span_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    span_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    highlighted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    region_box: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {x, y, width, height} for images/PDFs
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    source_ref: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "Guideline §2.1" or "Fact: Market share"
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 0.0 - 1.0
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)  # open, accepted, rejected, disputed, overridden
    guideline_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    submission: Mapped["ContentSubmission"] = relationship("ContentSubmission", back_populates="findings")
    rule: Mapped["GuidelineRule"] = relationship("GuidelineRule", back_populates="findings")
