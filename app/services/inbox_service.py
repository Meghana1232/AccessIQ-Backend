from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import InboxMessage, User


def create_message(
    db: Session,
    sender_employee_id: str,
    receiver_employee_id: str,
    subject: str,
    message: str
):
    # Check sender
    sender = db.query(User).filter(
        User.employee_id == sender_employee_id
    ).first()

    if not sender:
        raise HTTPException(
            status_code=404,
            detail="Sender not found."
        )

    # Check receiver
    receiver = db.query(User).filter(
        User.employee_id == receiver_employee_id
    ).first()

    if not receiver:
        raise HTTPException(
            status_code=404,
            detail="Receiver not found."
        )

    # Validate subject
    if not subject.strip():
        raise HTTPException(
            status_code=400,
            detail="Subject cannot be empty."
        )

    # Validate message
    if not message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    new_message = InboxMessage(
        sender_employee_id=sender_employee_id,
        receiver_employee_id=receiver_employee_id,
        subject=subject,
        message=message
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message

def get_received_messages(
    db: Session,
    employee_id: str
):
    messages = (
        db.query(InboxMessage)
        .filter(
            InboxMessage.receiver_employee_id == employee_id,
            InboxMessage.is_deleted_by_receiver == False
        )
        .order_by(
            InboxMessage.created_at.desc()
        )
        .all()
    )

    return messages

def get_message(
    db: Session,
    message_id: int,
    employee_id: str
):
    message = (
        db.query(InboxMessage)
        .filter(
            InboxMessage.id == message_id,
            InboxMessage.receiver_employee_id == employee_id
        )
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found."
        )

    return message

def mark_message_as_read(
    db: Session,
    message_id: int,
    employee_id: str
):
    message = (
        db.query(InboxMessage)
        .filter(
            InboxMessage.id == message_id,
            InboxMessage.receiver_employee_id == employee_id
        )
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found."
        )

    message.is_read = True

    db.commit()
    db.refresh(message)

    return {
        "message": "Message marked as read.",
        "message_id": message.id,
        "is_read": message.is_read
    }

def get_sent_messages(
    db: Session,
    employee_id: str
):
    messages = (
        db.query(InboxMessage)
        .filter(
            InboxMessage.sender_employee_id == employee_id,
            InboxMessage.is_deleted_by_sender == False
        )
        .order_by(
            InboxMessage.created_at.desc()
        )
        .all()
    )

    return messages

def delete_message(
    db: Session,
    message_id: int,
    employee_id: str
):
    message = (
        db.query(InboxMessage)
        .filter(
            InboxMessage.id == message_id
        )
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found."
        )

    if message.sender_employee_id == employee_id:
        message.is_deleted_by_sender = True

    elif message.receiver_employee_id == employee_id:
        message.is_deleted_by_receiver = True

    else:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this message."
        )

    if (
        message.is_deleted_by_sender
        and message.is_deleted_by_receiver
    ):
        db.delete(message)

    db.commit()

    return {
        "message": "Message deleted successfully.",
        "message_id": message_id
    }