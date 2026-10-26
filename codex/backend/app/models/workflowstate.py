"""WorkflowState, Comment, AuditLog, and ApprovalOverride models."""

import uuid
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, TenantMixin


class WorkflowState(Base, TimestampMixin, TenantMixin):
    """Workflow state transitions for a content submission."""

    __tablename__ = "workflow_states"

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
    from_state: Mapped[str] = mapped_column(String(50), nullable=False)
    to_state: Mapped[str] = mapped_column(String(50), nullable=False)
    transition_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    submission: Mapped["ContentSubmission"] = relationship("ContentSubmission", back_populates="workflow_states")
    actor: Mapped["User"] = relationship("User")


class Comment(Base, TimestampMixin, TenantMixin):
    """Threaded comments and discussion on a submission."""

    __tablename__ = "comments"

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
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    submission: Mapped["ContentSubmission"] = relationship("ContentSubmission", back_populates="comments")
    user: Mapped["User"] = relationship("User", back_populates="comments")
    replies: Mapped[list["Comment"]] = relationship("Comment", cascade="all, delete-orphan")


class AuditLog(Base, TimestampMixin, TenantMixin):
    """Immutable audit log of all system changes and approval actions."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)     # e.g., "SUBMISSION_APPROVED", "OVERRIDE_RECORDED"
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "submission", "rule", "finding"
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")


class ApprovalOverride(Base, TimestampMixin, TenantMixin):
    """Approval override record for findings waived or dismissed by an approver."""

    __tablename__ = "approval_overrides"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    finding_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("review_findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approver_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    finding: Mapped["ReviewFinding"] = relationship("ReviewFinding")
    approver: Mapped["User"] = relationship("User")
