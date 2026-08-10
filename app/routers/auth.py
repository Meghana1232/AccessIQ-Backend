from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserLogin
from app.services.auth_service import register_user, login_user

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
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register Employee",
    description="Registers a new employee for the AccessIQ system."
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return register_user(db, user)


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