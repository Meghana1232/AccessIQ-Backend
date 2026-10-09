import os
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import User, LoginHistory, InboxMessage, Alert


def get_all_users(db: Session):
    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )


def get_user(db: Session, employee_id: str):
    user = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return user


def update_user_role(db: Session, employee_id: str, role: str):
    role = role.strip().lower()

    if role not in ("employee", "admin"):
        raise HTTPException(
            status_code=400,
            detail="Role must be 'employee' or 'admin'."
        )

    user = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    user.role = role

    db.commit()
    db.refresh(user)

    return {
        "message": "Role updated successfully.",
        "employee_id": user.employee_id,
        "role": user.role
    }


def delete_user(db: Session, employee_id: str):
    """
    Permanently deletes an employee, along with their login history,
    inbox messages (sent and received), alerts, and stored face image.
    This cannot be undone.
    """

    user = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    face_path = user.face_image_path

    # Remove dependent rows first (no ON DELETE CASCADE configured
    # on these foreign keys, so this must be done manually)
    db.query(LoginHistory).filter(
        LoginHistory.employee_id == employee_id
    ).delete()

    db.query(InboxMessage).filter(
        (InboxMessage.sender_employee_id == employee_id)
        | (InboxMessage.receiver_employee_id == employee_id)
    ).delete()

    db.query(Alert).filter(
        Alert.employee_id == employee_id
    ).delete()

    db.delete(user)
    db.commit()

    if face_path and os.path.exists(face_path):
        os.remove(face_path)

    return {
        "message": "Employee deleted successfully.",
        "employee_id": employee_id
    }


def get_admin_stats(db: Session):
    today = datetime.now(timezone.utc).date()

    total_users = db.query(User).count()

    successful_logins_today = (
        db.query(LoginHistory)
        .filter(
            func.date(LoginHistory.login_time) == today,
            LoginHistory.login_status == "Success"
        )
        .count()
    )

    failed_logins_today = (
        db.query(LoginHistory)
        .filter(
            func.date(LoginHistory.login_time) == today,
            LoginHistory.login_status != "Success"
        )
        .count()
    )

    unread_alerts = (
        db.query(Alert)
        .filter(Alert.is_read.is_(False))
        .count()
    )

    unread_messages = (
        db.query(InboxMessage)
        .filter(InboxMessage.is_read.is_(False))
        .count()
    )

    return {
        "total_users": total_users,
        "successful_logins_today": successful_logins_today,
        "failed_logins_today": failed_logins_today,
        "unread_alerts": unread_alerts,
        "unread_messages": unread_messages
    }


def broadcast_alert(db: Session, title: str, message: str):
    title = title.strip()
    message = message.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Alert title cannot be empty."
        )

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Alert message cannot be empty."
        )

    users = db.query(User).all()

    for user in users:
        db.add(Alert(
            employee_id=user.employee_id,
            title=title,
            message=message
        ))

    db.commit()

    return {
        "message": "Alert broadcast successfully.",
        "recipients": len(users)
    }