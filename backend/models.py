"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The question to ask about the indexed PDFs"
    )

    @field_validator('question')
    @classmethod
    def question_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty or whitespace only')
        return v.strip()


class UploadResponse(BaseModel):
    """Response model for PDF upload"""
    status: str
    filename: str
    chunks_count: int = None
    message: str = None


class AskResponse(BaseModel):
    """Response model for question answering"""
    question: str
    answer: str
    context_used: list[str] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: str = None
    status_code: int
