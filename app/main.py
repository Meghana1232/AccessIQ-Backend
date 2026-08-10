from fastapi import FastAPI
from app.database import Base, engine
from app import models

# Import the router
from app.routers import auth, face

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AccessIQ API",
    description="Backend for Face Recognition Login System",
    version="1.0.0"
)

# Include the router
app.include_router(auth.router)
app.include_router(face.router)

@app.get("/")
def home():
    return {
        "message": "Welcome to AccessIQ Backend!"
    }