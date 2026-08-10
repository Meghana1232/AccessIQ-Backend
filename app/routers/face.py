from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate
from app.services.face_service import register_face

router = APIRouter(
    prefix="/face",
    tags=["Face Registration"]
)


@router.post("/register")
def face_register(
    employee_id: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    user = UserCreate(
        employee_id=employee_id,
        full_name=full_name,
        email=email
    )

    return register_face(db, user, image)