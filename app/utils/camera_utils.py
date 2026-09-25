import cv2
from fastapi import HTTPException


def capture_frame_from_webcam(save_path: str, warm_up_frames: int = 5):
    """
    Opens the webcam attached to the machine running this backend,
    captures a single frame, and saves it to save_path.

    NOTE: this only works because the server and the camera are on the
    same physical machine (local development). It will not work once
    the backend is deployed to a remote server with no camera attached.
    In that case, capture must happen in the browser and be uploaded
    instead — see the existing /face/register and /auth/login routes.
    """

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise HTTPException(
            status_code=500,
            detail="Unable to access webcam on this machine."
        )

    try:
        # Skip a few frames first so the camera's exposure/focus
        # can settle before we capture the real frame
        for _ in range(warm_up_frames):
            cap.read()

        ret, frame = cap.read()

        if not ret:
            raise HTTPException(
                status_code=500,
                detail="Failed to capture frame from webcam."
            )

        cv2.imwrite(save_path, frame)

    finally:
        cap.release()