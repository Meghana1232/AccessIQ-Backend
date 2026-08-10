from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate

import os
import shutil
import numpy as np
import face_recognition


# ---------------------------------------------------
# Register User (Keep this until registration is moved
# completely to face_service.py)
# ---------------------------------------------------
def register_user(db: Session, user: UserCreate):

    existing_user = db.query(User).filter(
        User.employee_id == user.employee_id
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists."
        )

    new_user = User(
        employee_id=user.employee_id,
        full_name=user.full_name,
        email=user.email,
        face_registered=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User details saved successfully.",
        "employee_id": new_user.employee_id
    }


# ---------------------------------------------------
# Login User
# ---------------------------------------------------
def login_user(
    db: Session,
    employee_id: str,
    image: UploadFile
):

    # Check employee
    existing_user = db.query(User).filter(
        User.employee_id == employee_id
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    if existing_user.face_encoding is None:
        raise HTTPException(
            status_code=400,
            detail="Face is not registered."
        )

    # Create temporary folder
    os.makedirs("temp", exist_ok=True)

    image_path = f"temp/{employee_id}_login.jpg"

    # Save uploaded image
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Load image
    captured_image = face_recognition.load_image_file(image_path)

    # Detect face
    face_locations = face_recognition.face_locations(captured_image)

    if len(face_locations) == 0:
        os.remove(image_path)
        raise HTTPException(
            status_code=400,
            detail="No face detected."
        )

    if len(face_locations) > 1:
        os.remove(image_path)
        raise HTTPException(
            status_code=400,
            detail="Multiple faces detected."
        )

    # Generate encoding
    captured_encoding = face_recognition.face_encodings(
        captured_image,
        face_locations
    )[0]

    # Convert stored encoding
    stored_encoding = np.frombuffer(
        existing_user.face_encoding,
        dtype=np.float64
    )

    # Compare faces
    match = face_recognition.compare_faces(
        [stored_encoding],
        captured_encoding,
        tolerance=0.5
    )

    # Remove temporary image
    os.remove(image_path)

    if not match[0]:
        raise HTTPException(
            status_code=401,
            detail="Face does not match."
        )

    return {
        "message": "Login Successful",
        "employee_id": existing_user.employee_id,
        "full_name": existing_user.full_name,
        "email": existing_user.email
    }