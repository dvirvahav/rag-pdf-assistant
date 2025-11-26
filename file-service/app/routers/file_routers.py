from fastapi import APIRouter, UploadFile, File
from app.services.file_service import (
    save_file,
    list_files,
    delete_file,
)

# API router for all file-management endpoints.
router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a new file to the storage service.
    Returns status + filename (no direct paths for security).
    """
    return save_file(file)


@router.get("/")
async def get_all_files():
    """
    Returns a list of all stored files.
    """
    return {"files": list_files()}


@router.delete("/{filename}")
async def delete_file_route(filename: str):
    """
    Delete a file from storage by name.
    """
    return delete_file(filename)
