import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas import AntiSpoofingResponse
from app.services.anti_spoofing_service import validate_face_input


router = APIRouter(
    prefix="/anti-spoofing",
    tags=["Anti-Spoofing"]
)


@router.post(
    "/validate",
    response_model=AntiSpoofingResponse,
    summary="Validate a face image",
    description="Standalone check for face presence, quality, and single-face "
                "requirements. Runs the same validation used internally by "
                "registration and login, callable independently for testing "
                "or client-side pre-checks."
)
def validate_face(
    image: UploadFile = File(...)
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

    # Unique filename per request, avoids collisions between
    # concurrent validation requests
    image_path = f"temp/validate_{uuid.uuid4().hex}.jpg"

    try:
        # Save uploaded image temporarily
        with open(image_path, "wb") as buffer:
            buffer.write(image.file.read())

        # Run the shared anti-spoofing / face-quality validation
        captured_image, face_locations, captured_encoding = validate_face_input(
            image_path
        )

        height, width = captured_image.shape[:2]

        return {
            "message": "Face image is valid.",
            "face_detected": True,
            "image_width": width,
            "image_height": height
        }

    finally:
        # Remove temporary image
        if os.path.exists(image_path):
            os.remove(image_path)