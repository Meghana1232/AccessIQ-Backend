from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import models
from app.schemas import UserCreate

import os
import shutil

import face_recognition
import numpy as np

def register_face(db: Session, user: UserCreate, image: UploadFile):

    # Check if employee ID already exists
    existing_user = db.query(models.User).filter(
        models.User.employee_id == user.employee_id
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists."
        )

    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists."
        )
       
    # Create folder if it doesn't exist
    os.makedirs("face_data", exist_ok=True)

    # Image path
    image_path = f"face_data/{user.employee_id}.jpg"

    # Save uploaded image
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Load the saved image
    captured_image = face_recognition.load_image_file(image_path)

    # Detect faces
    face_locations = face_recognition.face_locations(captured_image)

    # No face found
    if len(face_locations) == 0:
     raise HTTPException(
        status_code=400,
        detail="No face detected. Please capture your face properly."
    )

    # Multiple faces found
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

# --------------------------------------------------
# Compare with already registered users
# --------------------------------------------------

    registered_users = db.query(models.User).filter(
    models.User.face_encoding.isnot(None)
).all()

    for registered_user in registered_users:

     stored_encoding = np.frombuffer(
        registered_user.face_encoding,
        dtype=np.float64
    )

     match = face_recognition.compare_faces(
        [stored_encoding],
        captured_encoding,
        tolerance=0.5
    )

     if match[0]:
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

    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Face registered successfully.",
        "employee_id": new_user.employee_id,
        "full_name": new_user.full_name
    }    