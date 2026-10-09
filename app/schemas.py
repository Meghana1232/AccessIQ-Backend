import re
from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator


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


# Allowed gender values. The frontend dropdown shows friendly labels
# and sends one of these.
GenderOption = Literal["male", "female", "other", "prefer_not_to_say"]


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    full_name: str
    email: str
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None


class ProfileUpdate(BaseModel):
    # Every field is optional; only the ones sent are changed.
    full_name: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[date] = None      # format: YYYY-MM-DD
    phone_number: Optional[str] = None        # blank string clears it
    gender: Optional[GenderOption] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value is None:
            return value

        if value > date.today():
            raise ValueError("Date of birth cannot be in the future.")

        if value.year < 1900:
            raise ValueError("Date of birth is not valid.")

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        if value is None:
            return value

        value = value.strip()

        # A blank value means "remove my phone number"
        if value == "":
            return value

        # Allow spaces and dashes when typing, store digits only
        cleaned = re.sub(r"[\s\-]", "", value)

        if not re.fullmatch(r"\+?\d{7,15}", cleaned):
            raise ValueError(
                "Phone number must have 7 to 15 digits, "
                "optionally starting with +."
            )

        return cleaned