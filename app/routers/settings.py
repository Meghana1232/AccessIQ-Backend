from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas import (
    SettingsUpdate,
    SettingsResponse,
    NotificationSettingsUpdate,
    SecuritySettingsUpdate,
    ProfileResponse,
    ProfileUpdate
)

from app.services.settings_service import (
    get_settings,
    update_settings,
    update_notifications,
    update_security,
    get_profile,
    update_profile,
    reset_settings
)

from app.utils.security import get_current_employee


router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)


# ---------------------------------------------------
# Get All Settings
# ---------------------------------------------------

@router.get(
    "/",
    response_model=SettingsResponse
)
def read_settings(
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return get_settings(
        db,
        employee_id
    )


# ---------------------------------------------------
# Update All Settings
# ---------------------------------------------------

@router.put(
    "/",
    response_model=SettingsResponse
)
def update_all_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return update_settings(
        db,
        employee_id,
        data
    )


# ---------------------------------------------------
# Update Notification Settings
# ---------------------------------------------------

@router.patch(
    "/notifications",
    response_model=SettingsResponse
)
def update_notification_settings(
    data: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return update_notifications(
        db,
        employee_id,
        data
    )


# ---------------------------------------------------
# Update Security Settings
# ---------------------------------------------------

@router.patch(
    "/security",
    response_model=SettingsResponse
)
def update_security_settings(
    data: SecuritySettingsUpdate,
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return update_security(
        db,
        employee_id,
        data
    )


# ---------------------------------------------------
# Get Profile
# ---------------------------------------------------

@router.get(
    "/profile",
    response_model=ProfileResponse
)
def read_profile(
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return get_profile(
        db,
        employee_id
    )


# ---------------------------------------------------
# Update Profile
# ---------------------------------------------------

@router.put(
    "/profile",
    response_model=ProfileResponse
)
def edit_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return update_profile(
        db,
        employee_id,
        data
    )


# ---------------------------------------------------
# Reset Settings
# ---------------------------------------------------

@router.post(
    "/reset",
    response_model=SettingsResponse
)
def reset_user_settings(
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return reset_settings(
        db,
        employee_id
    )