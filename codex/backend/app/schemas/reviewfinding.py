"""Pydantic schemas for ReviewFinding."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewFindingBase(BaseModel):
    category: str = Field(..., description="tone, claim, terminology, visual, accessibility, disclaimer")
    severity: str = Field(..., description="high, medium, low, advisory")
    span_start: int | None = None
    span_end: int | None = None
    highlighted_text: str | None = None
    region_box: dict | None = None
    explanation: str
    source_ref: str
    confidence: float = 1.0
    suggested_fix: str | None = None
    status: str = "open"
    guideline_version: int = 1


class ReviewFindingCreate(ReviewFindingBase):
    submission_id: uuid.UUID
    rule_id: uuid.UUID | None = None


class ReviewFindingUpdate(BaseModel):
    category: str | None = None
    severity: str | None = None
    explanation: str | None = None
    source_ref: str | None = None
    confidence: float | None = None
    suggested_fix: str | None = None
    status: str | None = None


class ReviewFindingRead(ReviewFindingBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    submission_id: uuid.UUID
    rule_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
