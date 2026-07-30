from pydantic import BaseModel, EmailStr
from typing import Optional

# -----------------------------
# User Registration
# -----------------------------
class UserCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    image: str


# -----------------------------
# User Login
# -----------------------------
class UserLogin(BaseModel):
    employee_id: str
    image: str


# -----------------------------
# Face Registration
# -----------------------------
class FaceRegistration(BaseModel):
    user_id: int


# -----------------------------
# User Response
# -----------------------------
class UserResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    email: EmailStr
    face_registered: bool

    class Config:
        from_attributes = True