from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from app.pipeline.rag_pipeline import ask_question
from common.auth.dependencies import get_current_user

router = APIRouter(prefix="/rag", tags=["RAG"])

class AskRequest(BaseModel):
    filename: str
    question: str

@router.post("/ask")
async def rag_query(
    body: AskRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Ask a question about a specific indexed file.
    Requires authentication.
    """
    result = ask_question(body.filename, body.question)
    result["queried_by"] = user.get("username")
    return result
