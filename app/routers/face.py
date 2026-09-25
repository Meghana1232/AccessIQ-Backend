from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import FaceRegisterResponse
from app.services.face_service import register_face, register_face_webcam
from app.utils.security import get_current_employee


router = APIRouter(
    prefix="/face"
)


@router.get("/protected", tags=["Authentication"])
def protected_face_route(
    employee_id: str = Depends(get_current_employee)
):
    return {
        "message": "Authenticated access granted.",
        "employee_id": employee_id
    }


@router.post("/register", response_model=FaceRegisterResponse, tags=["Face Registration"])
def face_register(
    full_name: str = Form(...),
    email: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return register_face(
        db=db,
        full_name=full_name,
        email=email,
        image=image
    )


@router.post(
    "/register-webcam",
    response_model=FaceRegisterResponse,
    tags=["Face Registration"],
    summary="Register a face using the server's webcam",
    description="Captures a frame directly from the webcam attached to the "
                "machine running this backend. Only works in local "
                "development where the server and camera are the same "
                "machine — will not work on a deployed remote server."
)
def face_register_webcam(
    full_name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    return register_face_webcam(
        db=db,
        full_name=full_name,
        email=email
    )