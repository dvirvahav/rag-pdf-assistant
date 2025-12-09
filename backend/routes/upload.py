"""
PDF upload endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from qdrant_client import QdrantClient
import os

from backend.tasks import process_pdf_upload_task
from backend.services.job_status import job_status_service
from backend.models import JobSubmissionResponse, JobStatusResponse, ErrorResponse
from backend.config import settings


router = APIRouter()


def ensure_qdrant_alive():
    """Check if Qdrant is running"""
    try:
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        client.get_collections()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Qdrant is not running. Please start Qdrant on {settings.QDRANT_HOST}:{settings.QDRANT_PORT}."
        )


def validate_pdf_file(file: UploadFile) -> None:
    """
    Validate uploaded file for type, size, and name.
    Raises HTTPException if validation fails.
    """
    # Check if file exists
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only PDF files are allowed. Got: {file_ext}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB. Got: {file_size / 1024 / 1024:.2f}MB"
        )
    
    # Sanitize filename (prevent path traversal)
    if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename. Filename cannot contain path separators"
        )


@router.post(
    "/upload",
    summary="Upload a PDF for async processing",
    description="Queues the PDF for processing. Returns a job ID that can be used to check processing status.",
    response_model=JobSubmissionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and queue a PDF file for processing"""
    try:
        # Validate file before processing
        validate_pdf_file(file)
        ensure_qdrant_alive()

        # Read file content
        file_content = await file.read()

        # Create job metadata
        metadata = {
            "filename": file.filename,
            "file_size": len(file_content),
            "content_type": file.content_type
        }

        # Create job
        job_id = job_status_service.create_job("pdf_upload", metadata)

        # Prepare task data
        task_data = {
            "filename": file.filename,
            "content": file_content
        }

        # Submit task to Celery
        process_pdf_upload_task.delay(job_id, task_data)

        return JobSubmissionResponse(
            job_id=job_id,
            status="queued",
            message="PDF upload job queued successfully"
        )

    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue PDF processing: {str(e)}"
        )


@router.get(
    "/job/{job_id}",
    summary="Get job status",
    description="Check the status of a PDF processing job.",
    response_model=JobStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_job_status(job_id: str):
    """Get the status of a processing job"""
    try:
        job_data = job_status_service.get_job(job_id)

        if not job_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        return JobStatusResponse(**job_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )
