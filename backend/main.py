from fastapi import FastAPI, UploadFile, File
from pipeline.pdf_pipeline import process_pdf_upload

app = FastAPI()

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    result = process_pdf_upload(file)
    return result
