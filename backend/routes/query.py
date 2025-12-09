"""
RAG query endpoints
"""
from fastapi import APIRouter, HTTPException, status
from qdrant_client import QdrantClient

from backend.pipeline.rag_pipeline import process_question
from backend.models import AskRequest, AskResponse, ErrorResponse
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


@router.post(
    "/ask",
    summary="Ask a question about indexed PDFs",
    description="Embeds the question, retrieves relevant chunks from Qdrant, and generates an answer using GPT.",
    response_model=AskResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid question"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def ask_question(body: AskRequest):
    """Ask a question about the indexed documents"""
    try:
        ensure_qdrant_alive()
        
        # Process the question
        result = process_question(body.question)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (already have proper status codes)
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )
