import os
import uuid
from fastapi import UploadFile, HTTPException
from app.config import STORAGE_PATH
from app.services.rabbitmq_publisher import publish_file_uploaded_event
from app.services.redis_service import set_job_status


def save_file(file: UploadFile):
    """
    Save the uploaded file to the storage directory.
    Returns a structured response with job_id, status, and filename.

    This service handles file storage and initiates the embedding pipeline.
    After successful save:
    1. Generates a unique job_id
    2. Stores initial status "processing" in Redis
    3. Publishes event to RabbitMQ for embedding service
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    filepath = os.path.join(STORAGE_PATH, file.filename)

    try:
        # Write file in binary mode
        with open(filepath, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {e}"
        )

    # Set initial job status in Redis
    set_job_status(job_id, "processing", {"filename": file.filename})

    # Publish event to RabbitMQ for embedding service to process
    publish_file_uploaded_event(job_id, file.filename, filepath)

    return {
        "job_id": job_id,
        "status": "processing",
        "filename": file.filename
    }


def list_files():
    """
    Return all files in the storage directory.
    """
    try:
        return [
            f for f in os.listdir(STORAGE_PATH)
            if os.path.isfile(os.path.join(STORAGE_PATH, f))
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not list files: {e}"
        )


def delete_file(filename: str):
    """
    Delete a file from disk by name.
    Raises 404 if file does not exist.
    """
    filepath = os.path.join(STORAGE_PATH, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(filepath)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {e}"
        )

    return {
        "status": "deleted",
        "filename": filename
    }
