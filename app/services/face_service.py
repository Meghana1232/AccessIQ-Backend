from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import models
from app.schemas import UserCreate

import os
import shutil
import face_recognition
import numpy as np
import re

def register_face(db: Session, user: UserCreate, image: UploadFile):
    # Validate Employee ID format
    if not re.fullmatch(r"GT-\d{3}", user.employee_id):
        raise HTTPException(
        status_code=400,
        detail="Employee ID must be in GT-000 format. Example: GT-001."
    )


    # Validate Full Name
    if not re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", user.full_name.strip()):
        raise HTTPException(
        status_code=400,
        detail="Full name must contain only letters and spaces."
    )

    # Check if Employee ID already exists
    existing_user = db.query(models.User).filter(
        models.User.employee_id == user.employee_id
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists."
        )

    # Check if Email already exists
    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )

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

    # Create folder
    os.makedirs("face_data", exist_ok=True)

    # Image path
    image_path = f"face_data/{user.employee_id}.jpg"

    # Save image
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    try:
        # Load image
        captured_image = face_recognition.load_image_file(image_path)

        # Detect faces
        face_locations = face_recognition.face_locations(
            captured_image
        )

        # No face
        if len(face_locations) == 0:
            raise HTTPException(
                status_code=400,
                detail="No face detected. Please capture your face properly."
            )

        # Multiple faces
        if len(face_locations) > 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple faces detected. Please capture only one face."
            )

        # Generate face encoding
        captured_encoding = face_recognition.face_encodings(
            captured_image,
            face_locations
        )[0]

        # Convert encoding to bytes
        encoding_bytes = captured_encoding.tobytes()

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

            print("Face distance:", distance)

            match = distance < 0.45

            if match:
                raise HTTPException(
                    status_code=400,
                    detail="User already registered."
    )
        # Create new user
        new_user = models.User(
            employee_id=user.employee_id,
            full_name=user.full_name,
            email=user.email,
            face_image_path=image_path,
            face_encoding=encoding_bytes,
            face_registered=True
        )

        # Save to PostgreSQL
        db.add(new_user)

        try:
            db.commit()
            db.refresh(new_user)

        except SQLAlchemyError:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to store face registration data."
            )

        return {
            "message": "Face registered successfully.",
            "employee_id": new_user.employee_id,
            "full_name": new_user.full_name
        }

    except HTTPException:
        # Remove image if registration fails
        if os.path.exists(image_path):
            os.remove(image_path)

        raise