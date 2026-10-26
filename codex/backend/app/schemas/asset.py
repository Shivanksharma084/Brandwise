"""Pydantic schemas for Asset."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AssetBase(BaseModel):
    name: str
    asset_type: str = Field(..., description="logo, palette, font, template, image")
    file_path: str
    metadata_: dict = Field(default_factory=dict, serialization_alias="metadata")


class AssetCreate(AssetBase):
    workspace_id: uuid.UUID


class AssetUpdate(BaseModel):
    name: str | None = None
    asset_type: str | None = None
    file_path: str | None = None
    metadata_: dict | None = Field(None, serialization_alias="metadata")


class AssetRead(AssetBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
