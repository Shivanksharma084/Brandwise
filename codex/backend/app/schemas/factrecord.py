"""Pydantic schemas for FactRecord and TerminologyEntry."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class FactRecordBase(BaseModel):
    statistic: str
    value: str
    source_url: str | None = None
    owner: str
    valid_until: datetime
    notes: str | None = None


class FactRecordCreate(FactRecordBase):
    workspace_id: uuid.UUID


class FactRecordUpdate(BaseModel):
    statistic: str | None = None
    value: str | None = None
    source_url: str | None = None
    owner: str | None = None
    valid_until: datetime | None = None
    notes: str | None = None


class FactRecordRead(FactRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    verified_at: datetime
    created_at: datetime
    updated_at: datetime


class TerminologyEntryBase(BaseModel):
    term: str
    status: str = Field(..., description="preferred, banned")
    category: str | None = None
    preferred_alternative: str | None = None
    examples: list[str] = []
    notes: str | None = None


class TerminologyEntryCreate(TerminologyEntryBase):
    workspace_id: uuid.UUID


class TerminologyEntryUpdate(BaseModel):
    term: str | None = None
    status: str | None = None
    category: str | None = None
    preferred_alternative: str | None = None
    examples: list[str] | None = None
    notes: str | None = None


class TerminologyEntryRead(TerminologyEntryBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
