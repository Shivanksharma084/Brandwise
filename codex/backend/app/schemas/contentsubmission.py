"""Pydantic schemas for ContentSubmission."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ContentSubmissionBase(BaseModel):
    title: str = Field(..., max_length=255)
    text_content: str | None = None
    file_path: str | None = None
    file_type: str | None = Field(None, description="text, image, pdf, docx")
    channel: str | None = Field(None, description="social, blog, email, ad")
    campaign: str | None = None
    is_ai_assisted: bool = False


class ContentSubmissionCreate(ContentSubmissionBase):
    workspace_id: uuid.UUID
    creator_id: uuid.UUID
    status: str = "draft"
    version: int = 1


class ContentSubmissionUpdate(BaseModel):
    title: str | None = None
    text_content: str | None = None
    file_path: str | None = None
    channel: str | None = None
    campaign: str | None = None
    is_ai_assisted: bool | None = None


class ContentSubmissionRead(ContentSubmissionBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    creator_id: uuid.UUID
    status: str
    version: int
    metadata_: dict = Field(..., serialization_alias="metadata")
    created_at: datetime
    updated_at: datetime
