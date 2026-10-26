"""InsightMetric schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class InsightMetricBase(BaseModel):
    metric_type: str
    metric_value: float
    dimensions: dict = Field(default_factory=dict)


class InsightMetricCreate(InsightMetricBase):
    pass


class InsightMetricUpdate(BaseModel):
    metric_type: str | None = None
    metric_value: float | None = None
    dimensions: dict | None = None


class InsightMetricRead(InsightMetricBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
