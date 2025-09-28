from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class AttachmentPayload(BaseModel):
    filename: Optional[str] = Field(None, description="Name of the attachment file")
    contentBase64: Optional[str] = Field(None, description="Base64 encoded file content")


class EmailIntakePayload(BaseModel):
    subject: Optional[str] = Field(None, description="Email subject line")
    from_email: Optional[str] = Field(None, description="Email sender address")
    received_at: Optional[str] = Field(None, description="Email received timestamp")
    body: Optional[str] = Field(None, description="Email body content")
    attachments: List[AttachmentPayload] = Field(default_factory=list, description="List of email attachments")


class EmailIntakeResponse(BaseModel):
    submission_ref: str
    submission_id: int
    status: str
    message: str


class SubmissionResponse(BaseModel):
    id: int
    submission_id: int
    submission_ref: str
    subject: str
    sender_email: str
    body_text: Optional[str] = None
    extracted_fields: Optional[Dict[str, Any]] = None
    assigned_to: Optional[str] = None
    task_status: str
    created_at: datetime


class SubmissionConfirmRequest(BaseModel):
    underwriter_email: Optional[str] = None


class SubmissionConfirmResponse(BaseModel):
    submission_id: int
    submission_ref: str
    work_item_id: int
    assigned_to: str
    task_status: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
