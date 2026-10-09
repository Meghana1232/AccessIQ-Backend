from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User, UserSettings
from app.schemas import (
    SettingsUpdate,
    NotificationSettingsUpdate,
    SecuritySettingsUpdate,
    ProfileUpdate
)


def get_or_create_settings(
    db: Session,
    employee_id: str
):

    settings = (
        db.query(UserSettings)
        .filter(
            UserSettings.employee_id == employee_id
        )
        .first()
    )

    if not settings:

        settings = UserSettings(
            employee_id=employee_id,
            email_notifications=True,
            security_alerts=True,
            login_alerts=True
        )

        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


# ------------------------------------------------
# GET ALL SETTINGS
# ------------------------------------------------

def get_settings(
    db: Session,
    employee_id: str
):

    return get_or_create_settings(
        db,
        employee_id
    )


# ------------------------------------------------
# UPDATE ALL SETTINGS
# ------------------------------------------------

def update_settings(
    db: Session,
    employee_id: str,
    data: SettingsUpdate
):

    settings = get_or_create_settings(
        db,
        employee_id
    )

    settings.email_notifications = data.email_notifications
    settings.security_alerts = data.security_alerts
    settings.login_alerts = data.login_alerts

    db.commit()
    db.refresh(settings)

    return settings


# ------------------------------------------------
# UPDATE NOTIFICATION SETTINGS
# ------------------------------------------------

def update_notifications(
    db: Session,
    employee_id: str,
    data: NotificationSettingsUpdate
):

    settings = get_or_create_settings(
        db,
        employee_id
    )

    settings.email_notifications = (
        data.email_notifications
    )

    settings.login_alerts = (
        data.login_alerts
    )

    db.commit()
    db.refresh(settings)

    return settings


# ------------------------------------------------
# UPDATE SECURITY SETTINGS
# ------------------------------------------------

def update_security(
    db: Session,
    employee_id: str,
    data: SecuritySettingsUpdate
):

    settings = get_or_create_settings(
        db,
        employee_id
    )

    settings.security_alerts = (
        data.security_alerts
    )

    db.commit()
    db.refresh(settings)

    return settings


# ------------------------------------------------
# GET PROFILE
# ------------------------------------------------

def get_profile(
    db: Session,
    employee_id: str
):

    user = (
        db.query(User)
        .filter(
            User.employee_id == employee_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return user


# ------------------------------------------------
# UPDATE PROFILE
# ------------------------------------------------

def update_profile(
    db: Session,
    employee_id: str,
    data: ProfileUpdate
):

    if (
        data.full_name is None
        and data.email is None
        and data.date_of_birth is None
        and data.phone_number is None
        and data.gender is None
    ):

        raise HTTPException(
            status_code=400,
            detail="Provide at least one profile field to update"
        )

    user = (
        db.query(User)
        .filter(
            User.employee_id == employee_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    if data.full_name is not None:

        if not data.full_name.strip():

            raise HTTPException(
                status_code=400,
                detail="Full name cannot be empty"
            )

        user.full_name = data.full_name.strip()

    if data.email is not None:

        # Same normalization and format rule as registration,
        # so case variants can't slip past the duplicate check
        email = data.email.strip().lower()

        if "@" not in email or "." not in email.split("@")[-1]:

            raise HTTPException(
                status_code=400,
                detail="Invalid email address"
            )

        existing_user = (
            db.query(User)
            .filter(
                User.email == email,
                User.employee_id != employee_id
            )
            .first()
        )

        if existing_user:

            raise HTTPException(
                status_code=409,
                detail="Email already exists"
            )

        user.email = email

    if data.date_of_birth is not None:

        user.date_of_birth = data.date_of_birth

    if data.phone_number is not None:

        # Blank string removes the phone number
        user.phone_number = data.phone_number or None

    if data.gender is not None:

        user.gender = data.gender

    db.commit()
    db.refresh(user)

    return user


# ------------------------------------------------
# RESET SETTINGS
# ------------------------------------------------

def reset_settings(
    db: Session,
    employee_id: str
):

    settings = get_or_create_settings(
        db,
        employee_id
    )

    settings.email_notifications = True
    settings.security_alerts = True
    settings.login_alerts = True

    db.commit()
    db.refresh(settings)

    return settings