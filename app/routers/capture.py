from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.capture_service import capture_face


router = APIRouter(
    prefix="/capture",
    tags=["Face Capture"]
)


@router.post(
    "/face",
    summary="Capture and store employee face",
    description="Captures an employee's face, generates a face encoding, and stores the face data in PostgreSQL."
)
def capture(
    employee_id: str = Form(..., description="Employee ID"),
    image: UploadFile = File(..., description="Employee face image (JPG/PNG)"),
    db: Session = Depends(get_db)
):
    return capture_face(db, image, employee_id)