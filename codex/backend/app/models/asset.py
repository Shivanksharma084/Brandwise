"""Asset model for logos, palettes, fonts, and templates."""

import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, TenantMixin


class Asset(Base, TimestampMixin, TenantMixin):
    """Brand asset (logo, palette, font, template) stored in MinIO/S3."""

    __tablename__ = "assets"

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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)  # logo, palette, font, template
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    # metadata can store: colors (hex list), dimensions, format, font family, clear_space_px, etc.

    # Relationships
    workspace: Mapped["BrandWorkspace"] = relationship("BrandWorkspace", back_populates="assets")
