"""Pydantic schemas for GuidelineDocument and GuidelineRule."""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GuidelineDocumentBase(BaseModel):
    title: str
    file_path: str | None = None
    file_type: str | None = None
    version: int = 1
    is_active: bool = True


class GuidelineDocumentCreate(GuidelineDocumentBase):
    workspace_id: uuid.UUID


class GuidelineDocumentUpdate(BaseModel):
    title: str | None = None
    file_path: str | None = None
    file_type: str | None = None
    version: int | None = None
    is_active: bool | None = None


class GuidelineDocumentRead(GuidelineDocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class GuidelineRuleBase(BaseModel):
    clause_ref: str
    rule_type: str  # tone, terminology, messaging, disclaimer, visual, accessibility
    severity: str = "medium"  # high, medium, low, advisory
    channels: list[str] = []
    version: int = 1
    title: str
    description: str
    original_text: str | None = None
    is_active: bool = True


class GuidelineRuleCreate(GuidelineRuleBase):
    document_id: uuid.UUID


class GuidelineRuleUpdate(BaseModel):
    clause_ref: str | None = None
    rule_type: str | None = None
    severity: str | None = None
    channels: list[str] | None = None
    version: int | None = None
    title: str | None = None
    description: str | None = None
    original_text: str | None = None
    is_active: bool | None = None


class GuidelineRuleRead(GuidelineRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    document_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
