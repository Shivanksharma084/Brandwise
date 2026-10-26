"""Pydantic schemas for Tenant."""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TenantBase(BaseModel):
    name: str
    slug: str
    is_active: bool = True


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    is_active: bool | None = None


class TenantRead(TenantBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
