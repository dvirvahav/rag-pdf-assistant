from fastapi import FastAPI, HTTPException
from fastapi import UploadFile, File
from qdrant_client import QdrantClient
from pipeline.pdf_pipeline import process_pdf_upload
from pipeline.rag_pipeline import process_question
from pydantic import BaseModel
app = FastAPI()


class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(body: AskRequest):
    return process_question(body.question)

def ensure_qdrant_alive():
    try:
        client = QdrantClient(host="localhost", port=6333)
        client.get_collections()  
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Qdrant is not running. Please start Qdrant on port 6333."
        )

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    ensure_qdrant_alive()
    return process_pdf_upload(file)

@app.post("/ask")
async def ask_question(question: str):
    ensure_qdrant_alive()
    return process_question(question)
