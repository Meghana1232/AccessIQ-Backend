from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Alert, User


def create_alert(
    db: Session,
    employee_id: str,
    title: str,
    message: str
):
    # Check employee
    employee = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    # Validate title
    if not title.strip():
        raise HTTPException(
            status_code=400,
            detail="Alert title cannot be empty."
        )

    # Validate message
    if not message.strip():
        raise HTTPException(
            status_code=400,
            detail="Alert message cannot be empty."
        )

    new_alert = Alert(
        employee_id=employee_id,
        title=title.strip(),
        message=message.strip()
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return new_alert


def get_alerts(
    db: Session,
    employee_id: str
):
    alerts = (
        db.query(Alert)
        .filter(
            Alert.employee_id == employee_id
        )
        .order_by(
            Alert.created_at.desc()
        )
        .all()
    )

    return alerts


def mark_alert_as_read(
    db: Session,
    alert_id: int,
    employee_id: str
):
    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id,
            Alert.employee_id == employee_id
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found."
        )

    alert.is_read = True

    db.commit()
    db.refresh(alert)

    return {
        "message": "Alert marked as read.",
        "alert_id": alert.id,
        "is_read": alert.is_read
    }