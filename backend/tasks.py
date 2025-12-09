"""
Celery tasks for async processing
"""
from backend.celery_app import celery_app
from backend.services.job_status import job_status_service, JobStatus
from backend.services.storage import save_pdf
from backend.services.document_processing import extract_text_from_pdf, clean_text, chunk_text
from backend.services.embeddings import embed_chunks
from backend.services.vector_store import init_collection, is_file_indexed, upsert_chunks


@celery_app.task(bind=True)
def process_pdf_upload_task(self, job_id: str, file_data: dict):
    """
    Async task to process PDF upload with job status tracking
    """
    try:
        # Update job status to processing
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 10, "Initializing PDF processing"
        )

        # Extract file information from task data
        filename = file_data["filename"]
        file_content = file_data["content"]

        # Create a file-like object from the content
        from io import BytesIO
        file_obj = BytesIO(file_content)

        # Mock file object with filename attribute
        class MockFile:
            def __init__(self, content, filename):
                self.file = BytesIO(content)
                self.filename = filename

        mock_file = MockFile(file_content, filename)

        # Check that collection exists if not - create one
        init_collection()

        # Update progress
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 20, "Initializing collection"
        )

        # 1) Save file
        filepath = save_pdf(mock_file)
        filename = mock_file.filename

        # Update progress
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 30, "File saved successfully"
        )

        # 2) Skip if already processed
        if is_file_indexed(filename):
            result = {
                "status": "already_indexed",
                "filename": filename
            }
            job_status_service.update_job_status(
                job_id, JobStatus.COMPLETED, 100, "File already indexed", result=result
            )
            return result

        # Update progress
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 40, "Checking if file already indexed"
        )

        # 3) Extract text
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 50, "Extracting text from PDF"
        )
        raw_text = extract_text_from_pdf(filepath)

        # 4) Clean text
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 60, "Cleaning extracted text"
        )
        cleaned_text = clean_text(raw_text)

        # 5) Chunk text
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 70, "Chunking text"
        )
        chunks = chunk_text(cleaned_text)

        # 6) Embed chunks
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 80, "Generating embeddings"
        )
        vectors = embed_chunks(chunks)

        # 7) Save in Qdrant
        job_status_service.update_job_status(
            job_id, JobStatus.PROCESSING, 90, "Storing vectors in database"
        )
        upsert_chunks(vectors, chunks, filename)

        # Complete the job
        result = {
            "status": "indexed",
            "filename": filename,
            "chunks_count": len(chunks)
        }

        job_status_service.update_job_status(
            job_id, JobStatus.COMPLETED, 100, "PDF processing completed successfully", result=result
        )

        return result

    except Exception as e:
        # Update job status on failure
        error_msg = f"PDF processing failed: {str(e)}"
        job_status_service.update_job_status(
            job_id, JobStatus.FAILED, 0, error_msg, error=error_msg
        )
        raise  # Re-raise to mark task as failed
