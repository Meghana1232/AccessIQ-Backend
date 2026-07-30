from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserLogin

import base64
import os
import numpy as np
import face_recognition

# -----------------------------
# Register User
# -----------------------------
def register_user(db: Session, user: UserCreate):

    # Check if Employee ID already exists
    existing_employee = (
        db.query(User)
        .filter(User.employee_id == user.employee_id)
        .first()
    )

    if existing_employee:
        return {
            "success": False,
            "message": "Employee ID already exists"
        }

    # Check if Email already exists
    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        return {
            "success": False,
            "message": "Email already exists"
        }

    # Create folder to store face images
    os.makedirs("face_data", exist_ok=True)

    # Get Base64 image
    image_data = user.image

    # Remove Base64 header if present
    if "," in image_data:
        image_data = image_data.split(",")[1]

    # Decode Base64 string
    image_bytes = base64.b64decode(image_data)

    # Save image
    image_path = f"face_data/{user.employee_id}.jpg"

    with open(image_path, "wb") as file:
        file.write(image_bytes)

    # Load the saved image
    image = face_recognition.load_image_file(image_path)

    # Detect faces
    face_locations = face_recognition.face_locations(image)

    # Validate face
    if len(face_locations) == 0:
        os.remove(image_path)

        return {
            "success": False,
            "message": "No face detected. Please capture a clear face image."
        }

    # Create new user
    new_user = User(
        employee_id=user.employee_id,
        full_name=user.full_name,
        email=user.email,
        face_registered=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "success": True,
        "message": "User registered successfully",
        "user_id": new_user.id
    }
# -----------------------------
# Login User
# -----------------------------
def login_user(db: Session, user: UserLogin):

    existing_user = (
        db.query(User)
        .filter(User.employee_id == user.employee_id)
        .first()
    )

    if not existing_user:
        return {
            "success": False,
            "message": "Employee does not exist. Please register first."
        }
    # Decode Base64 image
    image_data = user.image

    # Remove Base64 header if present
    if "," in image_data:
        image_data = image_data.split(",")[1]

    image_bytes = base64.b64decode(image_data)

    # Save current login image
    login_image_path = f"face_data/login_{user.employee_id}.jpg"

    with open(login_image_path, "wb") as file:
        file.write(image_bytes)
    # Path of the registered image
    registered_image_path = f"face_data/{user.employee_id}.jpg"

    # Check if registered image exists
    if not os.path.exists(registered_image_path):
        return {
            "success": False,
            "message": "Registered face not found."
    }

    # Load images
    registered_image = face_recognition.load_image_file(registered_image_path)
    login_image = face_recognition.load_image_file(login_image_path)

    # Generate face encodings
    registered_encodings = face_recognition.face_encodings(registered_image)
    login_encodings = face_recognition.face_encodings(login_image)

    # Check if face is detected
    if len(registered_encodings) == 0:
         return {
         "success": False,
         "message": "No face found in registered image."
    }

    if len(login_encodings) == 0:
        return {
        "success": False,
        "message": "No face found in login image."
    }

# Compare faces
    match = face_recognition.compare_faces(
        [registered_encodings[0]],
        login_encodings[0]
)[0]

    if not match:
        return {
            "success": False,
            "message": "Face does not match."
    }

    return {
        "success": True,
        "message": "Login Successful",
        "user_id": existing_user.id,
        "employee_id": existing_user.employee_id,
        "full_name": existing_user.full_name,
        "email": existing_user.email,
        "face_registered": existing_user.face_registered
    }