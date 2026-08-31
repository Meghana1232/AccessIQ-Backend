from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models

from app.routers import auth, face, login_history


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AccessIQ API",
    description="Backend for Face Recognition Login System",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(face.router)
app.include_router(login_history.router)

@app.get("/")
def home():
    return {
        "message": "Welcome to AccessIQ Backend!"
    }