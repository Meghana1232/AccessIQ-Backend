import logging
import os
import shutil
import uuid

import face_recognition
import numpy as np
from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models
from app.services.anti_spoofing_service import validate_face_input
from app.utils.camera_utils import capture_frame_from_webcam

logger = logging.getLogger(__name__)


def _register_face_from_path(db: Session, full_name: str, email: str, image_path: str):
    """
    Shared registration logic once we already have an image saved on disk,
    regardless of whether it came from an upload or a webcam capture.
    """

    try:
        # Anti-Spoofing and security validation
        captured_image, face_locations, captured_encoding = validate_face_input(
            image_path
        )

        # Check duplicate face
        registered_users = db.query(models.User).filter(
            models.User.face_encoding.isnot(None)
        ).all()

        for registered_user in registered_users:

            stored_encoding = np.frombuffer(
                registered_user.face_encoding,
                dtype=np.float64
            )

            distance = face_recognition.face_distance(
                [stored_encoding],
                captured_encoding
            )[0]

            logger.debug("Face distance vs %s: %s", registered_user.employee_id, distance)

            if distance < 0.45:
                raise HTTPException(
                    status_code=400,
                    detail="This face is already registered."
                )

        # Get the next employee ID
        last_user = db.query(models.User).order_by(
            models.User.id.desc()
        ).first()

        if last_user and last_user.employee_id:
            last_number = int(
                last_user.employee_id.split("-")[1]
            )
            next_number = last_number + 1
        else:
            next_number = 1

        generated_employee_id = f"GT-{next_number:03d}"

        # Permanent face storage
        os.makedirs("face_data", exist_ok=True)

        permanent_image_path = (
            f"face_data/{generated_employee_id}.jpg"
        )

        shutil.copy(
            image_path,
            permanent_image_path
        )

        # Create user
        new_user = models.User(
            employee_id=generated_employee_id,
            full_name=full_name,
            email=email,
            face_image_path=permanent_image_path,
            face_encoding=captured_encoding.tobytes(),
            face_registered=True
        )

        # Save to PostgreSQL
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "Face registered successfully.",
            "employee_id": new_user.employee_id,
            "full_name": new_user.full_name,
            "email": new_user.email
        }

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to store face registration data."
        )

    except Exception as e:
        db.rollback()

        logger.exception("Registration error: %s", e)

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the face image."
        )


def register_face(db: Session, full_name: str, email: str, image: UploadFile):
    """
    Registration entrypoint for an uploaded image (existing flow).
    """

    # ------------------------------------------------
    # Validate full name
    # ------------------------------------------------
    full_name = full_name.strip()

    if not full_name:
        raise HTTPException(
            status_code=400,
            detail="Full name cannot be empty."
        )

    # ------------------------------------------------
    # Validate email (basic format check)
    # ------------------------------------------------
    email = email.strip().lower()

    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(
            status_code=400,
            detail="Invalid email address."
        )

    # ------------------------------------------------
    # Check email not already registered
    # ------------------------------------------------
    existing_email = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered."
        )

    # ------------------------------------------------
    # Validate image type
    # ------------------------------------------------
    allowed_types = ["image/jpeg", "image/png"]

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, or PNG images are allowed."
        )

    # ------------------------------------------------
    # Validate image size
    # ------------------------------------------------
    MAX_FILE_SIZE = 5 * 1024 * 1024

    image.file.seek(0, 2)
    file_size = image.file.tell()
    image.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 5 MB."
        )

    os.makedirs("temp", exist_ok=True)
    image_path = f"temp/register_{uuid.uuid4().hex}.jpg"

    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        return _register_face_from_path(db, full_name, email, image_path)

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


def register_face_webcam(db: Session, full_name: str, email: str):
    """
    Registration entrypoint that captures the image directly from the
    server's attached webcam instead of receiving an upload.

    Only works when the backend runs on the same machine as the camera
    (local development/demo). Will not work on a deployed remote server.
    """

    full_name = full_name.strip()

    if not full_name:
        raise HTTPException(
            status_code=400,
            detail="Full name cannot be empty."
        )

    email = email.strip().lower()

    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(
            status_code=400,
            detail="Invalid email address."
        )

    existing_email = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered."
        )

    os.makedirs("temp", exist_ok=True)
    image_path = f"temp/register_webcam_{uuid.uuid4().hex}.jpg"

    try:
        capture_frame_from_webcam(image_path)

        return _register_face_from_path(db, full_name, email, image_path)

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)