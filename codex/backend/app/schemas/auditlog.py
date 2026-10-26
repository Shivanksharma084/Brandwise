"""Pydantic schemas for AuditLog, WorkflowState, Comment, InsightMetric, GuidelineGap."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class WorkflowStateBase(BaseModel):
    from_state: str
    to_state: str
    notes: str | None = None


class WorkflowStateCreate(WorkflowStateBase):
    submission_id: uuid.UUID
    transition_by: uuid.UUID


class WorkflowStateRead(WorkflowStateBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    submission_id: uuid.UUID
    transition_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CommentBase(BaseModel):
    content: str
    parent_id: uuid.UUID | None = None


class CommentCreate(CommentBase):
    submission_id: uuid.UUID
    user_id: uuid.UUID


class CommentRead(CommentBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    submission_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: str
    details: dict = Field(default_factory=dict)


class AuditLogCreate(AuditLogBase):
    user_id: uuid.UUID | None = None


class AuditLogUpdate(BaseModel):
    action: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    details: dict | None = None


class AuditLogRead(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class GuidelineGapBase(BaseModel):
    override_rate: float = 0.0
    dispute_rate: float = 0.0
    recurring_count: int = 0
    suggested_clarification: str
    example_cases: list[dict] = []


class GuidelineGapCreate(GuidelineGapBase):
    rule_id: uuid.UUID


class GuidelineGapUpdate(BaseModel):
    override_rate: float | None = None
    dispute_rate: float | None = None
    recurring_count: int | None = None
    suggested_clarification: str | None = None
    example_cases: list[dict] | None = None


class GuidelineGapRead(GuidelineGapBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    rule_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
