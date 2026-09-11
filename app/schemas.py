from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------
# Face Registration
# ---------------------------------------------------
class FaceRegisterResponse(BaseModel):
    message: str
    employee_id: str
    full_name: str
    email: str


# ---------------------------------------------------
# Face Login
# ---------------------------------------------------
class LoginResponse(BaseModel):
    message: str
    employee_id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    access_token: str
    token_type: str


# ---------------------------------------------------
# Inbox
# ---------------------------------------------------
class InboxMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_employee_id: str
    receiver_employee_id: str
    subject: str
    message: str
    is_read: bool
    created_at: datetime


class MarkAsReadResponse(BaseModel):
    message: str
    message_id: int
    is_read: bool


# ---------------------------------------------------
# Login History
# ---------------------------------------------------
class LoginHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    login_time: datetime
    login_status: str
    login_method: str


class LoginHistoryResponse(BaseModel):
    employee_id: str
    login_history: List[LoginHistoryOut]