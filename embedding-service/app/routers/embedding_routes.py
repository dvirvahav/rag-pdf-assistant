from fastapi import APIRouter
from pydantic import BaseModel
from app.pipeline.pdf_pipeline import process_file

router = APIRouter(prefix="/embed", tags=["Embedding"])

class EmbeddingRequest(BaseModel):
    filename: str

@router.post("/")
async def embed_file(req: EmbeddingRequest):
    """
    Trigger the full embedding pipeline for a given file.
    """
    return process_file(req.filename)
