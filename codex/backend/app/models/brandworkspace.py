"""BrandWorkspace model."""

import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, TenantMixin


class BrandWorkspace(Base, TimestampMixin, TenantMixin):
    """Brand workspace containing guideline documents, rules, facts, terminology, and assets."""

    __tablename__ = "brand_workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="workspaces")
    guideline_documents: Mapped[list["GuidelineDocument"]] = relationship("GuidelineDocument", back_populates="workspace", cascade="all, delete-orphan")
    fact_records: Mapped[list["FactRecord"]] = relationship("FactRecord", back_populates="workspace", cascade="all, delete-orphan")
    terminology_entries: Mapped[list["TerminologyEntry"]] = relationship("TerminologyEntry", back_populates="workspace", cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="workspace", cascade="all, delete-orphan")
    submissions: Mapped[list["ContentSubmission"]] = relationship("ContentSubmission", back_populates="workspace", cascade="all, delete-orphan")
