from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.face_service import register_face
from app.utils.security import get_current_employee


router = APIRouter(
    prefix="/face",
    tags=["Face Registration"]
)


@router.get("/protected")
def protected_face_route(
    employee_id: str = Depends(get_current_employee)
):
    return {
        "message": "Authenticated access granted.",
        "employee_id": employee_id
    }


@router.post("/register")
def face_register(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return register_face(db, image)