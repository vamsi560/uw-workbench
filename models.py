from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class AttachmentModel(BaseModel):
    filename: str
    contentBase64: str


class EmailIntakeRequest(BaseModel):
    subject: str
    from_email: str  # Using from_email instead of 'from' as it's a Python keyword
    received_at: datetime
    body: str
    attachments: List[AttachmentModel] = []


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
