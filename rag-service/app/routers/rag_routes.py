from fastapi import APIRouter
from pydantic import BaseModel
from app.pipeline.rag_pipeline import ask_question

router = APIRouter(prefix="/rag", tags=["RAG"])

class AskRequest(BaseModel):
    filename: str
    question: str

@router.post("/ask")
async def rag_query(body: AskRequest):
    """
    Ask a question about a specific indexed file.
    """
    return ask_question(body.filename, body.question)
