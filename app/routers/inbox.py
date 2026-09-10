from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.inbox_service import (create_message, get_received_messages, get_sent_messages, get_message, mark_message_as_read)
from app.utils.security import get_current_employee


router = APIRouter(
    prefix="/inbox",
    tags=["Inbox"]
)


@router.post("/")
def send_message(
    receiver_employee_id: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
    sender_employee_id: str = Depends(get_current_employee)
):
    return create_message(
        db=db,
        sender_employee_id=sender_employee_id,
        receiver_employee_id=receiver_employee_id,
        subject=subject,
        message=message
    )


@router.get("/")
def get_inbox(
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return get_received_messages(
        db=db,
        employee_id=employee_id
    )


# IMPORTANT: /sent must come before /{message_id}
@router.get("/sent")
def get_sent(
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return get_sent_messages(
        db=db,
        employee_id=employee_id
    )


@router.get("/{message_id}")
def view_message(
    message_id: int,
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return get_message(
        db=db,
        message_id=message_id,
        employee_id=employee_id
    )


@router.put("/{message_id}/read")
def read_message(
    message_id: int,
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return mark_message_as_read(
        db=db,
        message_id=message_id,
        employee_id=employee_id
    )