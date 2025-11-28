from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import (
    save_file,
    list_files,
    delete_file,
)
from app.services.redis_service import get_job_status

# API router for all file-management endpoints.
router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a new file to the storage service.
    Returns job_id, status, and filename.
    The job_id can be used to poll for embedding completion status.
    """
    return save_file(file)


@router.get("/jobs/{job_id}/status")
async def get_job_status_route(job_id: str):
    """
    Get the status of an upload/embedding job.
    
    Returns:
        - status: "processing", "completed", or "failed"
        - details: Additional information (filename, error, chunks_count, etc.)
    """
    job_data = get_job_status(job_id)
    if job_data is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **job_data}


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
