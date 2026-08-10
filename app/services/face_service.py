from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import models
from app.schemas import UserCreate

import os
import shutil


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

    # Create folder if it doesn't exist
    os.makedirs("face_data", exist_ok=True)

    # Image path
    image_path = f"face_data/{user.employee_id}.jpg"

    # Save uploaded image
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return {
        "message": "Image uploaded successfully."
    }