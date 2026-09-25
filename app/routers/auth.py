from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import LoginResponse
from app.services.auth_service import login_user, login_user_webcam


router = APIRouter(
    prefix="/auth"
)


@router.get("/", tags=["Authentication"])
def auth_home():
    return {
        "message": "Authentication Router Working"
    }


@router.post(
    "/login",
    response_model=LoginResponse,
    tags=["Face Registration"],
    summary="Face Recognition Login",
    description="Authenticates an employee using face recognition."
)
def login(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return login_user(db, image)


@router.post(
    "/login-webcam",
    response_model=LoginResponse,
    tags=["Face Registration"],
    summary="Face Recognition Login via server webcam",
    description="Captures a frame directly from the webcam attached to the "
                "machine running this backend and authenticates against it. "
                "Only works in local development where the server and "
                "camera are the same machine — will not work on a deployed "
                "remote server."
)
def login_webcam(
    db: Session = Depends(get_db)
):
    return login_user_webcam(db)