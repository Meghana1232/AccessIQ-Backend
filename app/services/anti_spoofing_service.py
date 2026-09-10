from fastapi import HTTPException
import face_recognition
import numpy as np


def validate_face_input(image_path: str):
    """
    Validate uploaded face image before registration or login.
    """

    try:
        # Load image
        image = face_recognition.load_image_file(image_path)

        # Check image is not empty
        if image is None or image.size == 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid or empty image."
            )

        # Check image dimensions
        height, width = image.shape[:2]

        if width < 100 or height < 100:
            raise HTTPException(
                status_code=400,
                detail="Image resolution is too low."
            )

        # Detect faces
        face_locations = face_recognition.face_locations(image)

        # No face
        if len(face_locations) == 0:
            raise HTTPException(
                status_code=400,
                detail="No face detected. Please capture your face properly."
            )

        # Multiple faces
        if len(face_locations) > 1:
            raise HTTPException(
                status_code=400,
                detail="Multiple faces detected. Please capture only one face."
            )

        # Generate encoding
        encodings = face_recognition.face_encodings(
            image,
            face_locations
        )

        if not encodings:
            raise HTTPException(
                status_code=400,
                detail="Unable to process the face. Please try again."
            )

        return image, face_locations, encodings[0]

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or suspicious face image."
        )