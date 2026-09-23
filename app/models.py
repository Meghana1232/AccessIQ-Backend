from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base

from sqlalchemy import LargeBinary

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String, unique=True, nullable=False)

    full_name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    face_image_path = Column(String, nullable=True)

    face_encoding = Column(LargeBinary, nullable=True)

    face_registered = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        String,
        ForeignKey("users.employee_id"),
        nullable=False
    )

    login_time = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    login_status = Column(
        String,
        nullable=False
    )

    login_method = Column(
        String,
        nullable=False
    )


class InboxMessage(Base):
    __tablename__ = "inbox_messages"

    id = Column(Integer, primary_key=True, index=True)

    sender_employee_id = Column(
        String,
        ForeignKey("users.employee_id"),
        nullable=False
    )

    receiver_employee_id = Column(
        String,
        ForeignKey("users.employee_id"),
        nullable=False
    )

    subject = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        String,
        ForeignKey("users.employee_id"),
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )