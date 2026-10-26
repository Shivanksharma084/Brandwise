"""Pydantic schemas for BrandWorkspace."""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BrandWorkspaceBase(BaseModel):
    name: str
    description: str | None = None


class BrandWorkspaceCreate(BrandWorkspaceBase):
    pass


class BrandWorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class BrandWorkspaceRead(BrandWorkspaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
