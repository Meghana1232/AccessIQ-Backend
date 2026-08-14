from fastapi import APIRouter, Depends, UploadFile, File, Form
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
    summary="Employee Login",
    description="Authenticates an employee using Employee ID."
)
def login(
    employee_id: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return login_user(db, employee_id, image)