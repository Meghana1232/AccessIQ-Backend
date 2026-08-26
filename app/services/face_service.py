from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import models

import os
import shutil
import face_recognition
import numpy as np


def register_face(db: Session, image: UploadFile):

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

    # Create temporary folder
    os.makedirs("temp", exist_ok=True)

    image_path = "temp/registration_face.jpg"

    try:
        # Save uploaded image temporarily
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Load image
        captured_image = face_recognition.load_image_file(image_path)

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
        captured_encoding = face_recognition.face_encodings(
            captured_image,
            face_locations
        )[0]

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

        # Create user automatically
        new_user = models.User(
            employee_id=generated_employee_id,
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
            "employee_id": new_user.employee_id
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

        print("Registration error:", str(e))

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the face image."
        )

    finally:
        # Remove temporary image
        if os.path.exists(image_path):
            os.remove(image_path)