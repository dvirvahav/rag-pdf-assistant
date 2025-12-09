"""
API routes for the RAG PDF Assistant
"""
from fastapi import APIRouter
from .upload import router as upload_router
from .query import router as query_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(upload_router, prefix="/documents", tags=["Documents"])
api_router.include_router(query_router, prefix="/query", tags=["RAG Query"])

__all__ = ["api_router"]
