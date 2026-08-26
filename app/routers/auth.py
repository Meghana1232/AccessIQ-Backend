from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import login_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/")
def auth_home():
    return {
        "message": "Authentication Router Working"
    }


@router.post(
    "/login",
    summary="Face Recognition Login",
    description="Authenticates an employee using face recognition."
)
def login(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return login_user(db, image)