from fastapi import FastAPI
from app.routers.file_routers import router as file_router

# Application entrypoint for the File Service.
# Exposes REST endpoints for managing stored files (upload/list/delete).
app = FastAPI(
    title="File Service",
    description="Handles file upload, deletion, and listing.",
    version="1.0.0"
)

# Register file-related routes
app.include_router(file_router)
