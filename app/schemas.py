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
# Anti-Spoofing
# ---------------------------------------------------
class AntiSpoofingResponse(BaseModel):
    message: str
    face_detected: bool
    image_width: int
    image_height: int


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


class DeleteMessageResponse(BaseModel):
    message: str
    message_id: int


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


# ---------------------------------------------------
# Admin Panel
# ---------------------------------------------------
class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    full_name: str
    email: str
    role: str
    face_registered: bool
    created_at: Optional[datetime] = None


class RoleUpdateResponse(BaseModel):
    message: str
    employee_id: str
    role: str


class DeleteUserResponse(BaseModel):
    message: str
    employee_id: str


class AdminStatsResponse(BaseModel):
    total_users: int
    successful_logins_today: int
    failed_logins_today: int
    unread_alerts: int
    unread_messages: int


class BroadcastAlertResponse(BaseModel):
    message: str
    recipients: int

# ---------------------------------------------------
# Settings Module
# ---------------------------------------------------

class SettingsUpdate(BaseModel):
    email_notifications: bool
    security_alerts: bool
    login_alerts: bool


class NotificationSettingsUpdate(BaseModel):
    email_notifications: bool
    login_alerts: bool


class SecuritySettingsUpdate(BaseModel):
    security_alerts: bool


class SettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    email_notifications: bool
    security_alerts: bool
    login_alerts: bool


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    full_name: str
    email: str


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None 