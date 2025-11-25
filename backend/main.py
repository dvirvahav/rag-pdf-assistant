from fastapi import FastAPI, HTTPException, UploadFile, File
from qdrant_client import QdrantClient
from pydantic import BaseModel

from pipeline.pdf_pipeline import process_pdf_upload
from pipeline.rag_pipeline import process_question


app = FastAPI(
    title="📄 RAG PDF Assistant API",
    description="API for uploading PDF files, indexing them into Qdrant, and answering questions using Retrieval-Augmented Generation (RAG).",
    version="1.2.0"
)

# ---------------------------
# Models
# ---------------------------

class AskRequest(BaseModel):
    question: str


# ---------------------------
# Helpers
# ---------------------------

def ensure_qdrant_alive():
    try:
        client = QdrantClient(host="localhost", port=6333)
        client.get_collections()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Qdrant is not running. Please start Qdrant on port 6333."
        )


# ---------------------------
# Endpoints
# ---------------------------

@app.post(
    "/upload-pdf",
    tags=["PDF Upload"],
    summary="Upload a PDF and index it into Qdrant",
    description="Saves the PDF, extracts text, cleans it, chunks it, embeds it, and stores the vectors in Qdrant."
)
async def upload_pdf(file: UploadFile = File(...)):
    ensure_qdrant_alive()
    return process_pdf_upload(file)


@app.post(
    "/ask",
    tags=["RAG Query"],
    summary="Ask a question about indexed PDFs",
    description="Embeds the question, retrieves relevant chunks from Qdrant, and generates an answer using GPT."
)
async def ask_question(body: AskRequest):
    ensure_qdrant_alive()
    return process_question(body.question)
