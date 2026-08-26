from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import User
from app.utils.security import create_access_token
from app.services.login_history_service import create_login_history

import os
import shutil
import numpy as np
import face_recognition


# ---------------------------------------------------
# Face Login
# ---------------------------------------------------
def login_user(
    db: Session,
    image: UploadFile
):

    # Validate image type
    allowed_types = ["image/jpeg", "image/png"]

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, or PNG images are allowed."
        )

    # Create temporary folder
    os.makedirs("temp", exist_ok=True)

    image_path = "temp/login_face.jpg"

    try:
        # Save uploaded image
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Load image
        captured_image = face_recognition.load_image_file(image_path)

        # Detect faces
        face_locations = face_recognition.face_locations(
            captured_image
        )

        if len(face_locations) == 0:
            raise HTTPException(
                status_code=400,
                detail="No face detected."
            )

        if len(face_locations) > 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple faces detected."
            )

        # Generate live face encoding
        captured_encoding = face_recognition.face_encodings(
            captured_image,
            face_locations
        )[0]

        # Get all registered employees
        registered_users = db.query(User).filter(
            User.face_encoding.isnot(None)
        ).all()

        if not registered_users:
            raise HTTPException(
                status_code=404,
                detail="No registered faces found."
            )

        # Find closest matching face
        matched_user = None
        best_distance = float("inf")

        for user in registered_users:

            stored_encoding = np.frombuffer(
                user.face_encoding,
                dtype=np.float64
            )

            distance = face_recognition.face_distance(
                [stored_encoding],
                captured_encoding
            )[0]

            if distance < best_distance:
                best_distance = distance
                matched_user = user

        # Verify face match
        TOLERANCE = 0.5

        if matched_user is None or best_distance >= TOLERANCE:
            raise HTTPException(
                status_code=401,
                detail="Face not recognized."
            )
        # Create login history
        create_login_history(
            db=db,
            employee_id=matched_user.employee_id,
            login_status="Success",
            login_method="Face Recognition"
        )

        # Generate JWT token
        access_token = create_access_token(
            matched_user.employee_id
        )

        return {
            "message": "Login Successful",
            "employee_id": matched_user.employee_id,
            "full_name": matched_user.full_name,
            "email": matched_user.email,
            "access_token": access_token,
            "token_type": "bearer"
        }

    finally:
        # Remove temporary image
        if os.path.exists(image_path):
            os.remove(image_path)