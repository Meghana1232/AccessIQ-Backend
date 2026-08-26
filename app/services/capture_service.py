from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import models

import os
import shutil
import face_recognition
import numpy as np


def capture_face(
    db: Session,
    image: UploadFile,
    employee_id: str
):
    # Validate image type
    allowed_types = ["image/jpeg", "image/png"]

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, or PNG images are allowed."
        )

    # Validate image size
    MAX_FILE_SIZE = 5 * 1024 * 1024

    image.file.seek(0, 2)
    file_size = image.file.tell()
    image.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 5 MB."
        )

    # Find employee
    user = db.query(models.User).filter(
        models.User.employee_id == employee_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    if user.face_registered:
        raise HTTPException(
            status_code=400,
            detail="Face is already registered for this employee."
        )

    # Create storage folder
    os.makedirs("face_data", exist_ok=True)

    image_path = f"face_data/capture_{employee_id}.jpg"

    try:
        # Save captured image
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Load image
        captured_image = face_recognition.load_image_file(
            image_path
        )

        # Detect faces
        face_locations = face_recognition.face_locations(
            captured_image
        )

        # No face detected
        if len(face_locations) == 0:
            raise HTTPException(
                status_code=400,
                detail="No face detected. Please capture your face properly."
            )

        # Multiple faces detected
        if len(face_locations) > 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple faces detected. Please capture only one face."
            )

        # Generate face encoding
        face_encoding = face_recognition.face_encodings(
            captured_image,
            face_locations
        )[0]

        encoding_bytes = face_encoding.tobytes()

        # Check duplicate face
        registered_users = db.query(models.User).filter(
            models.User.face_encoding.isnot(None),
            models.User.id != user.id
        ).all()

        for registered_user in registered_users:

            stored_encoding = np.frombuffer(
                registered_user.face_encoding,
                dtype=np.float64
            )

            distance = face_recognition.face_distance(
                [stored_encoding],
                face_encoding
            )[0]

            if distance < 0.5:
                raise HTTPException(
                    status_code=400,
                    detail="This face is already registered to another employee."
                )

        # Store face data
        user.face_encoding = encoding_bytes
        user.face_image_path = image_path
        user.face_registered = True

        db.commit()
        db.refresh(user)

        return {
            "message": "Face captured and stored successfully.",
            "employee_id": user.employee_id,
            "face_registered": user.face_registered
        }

    except HTTPException:
        # Remove image when validation fails
        if os.path.exists(image_path):
            os.remove(image_path)

        raise

    except SQLAlchemyError:
        db.rollback()

        if os.path.exists(image_path):
            os.remove(image_path)

        raise HTTPException(
            status_code=500,
            detail="Failed to store face data in the database."
        )

    except Exception:
        db.rollback()

        if os.path.exists(image_path):
            os.remove(image_path)

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the face image."
        )