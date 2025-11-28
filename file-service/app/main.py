from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.file_routers import router as file_router

# Application entrypoint for the File Service.
# Exposes REST endpoints for managing stored files (upload/list/delete).
app = FastAPI(
    title="File Service",
    description="Handles file upload, deletion, and listing.",
    version="1.0.0"
)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register file-related routes
app.include_router(file_router)
