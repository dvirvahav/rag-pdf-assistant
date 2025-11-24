from fastapi import FastAPI, UploadFile, File, HTTPException
from utils.pdf_utils import extract_clean_text, chunk_text
from services.embedding_service import embed_text

app = FastAPI();


#define async function to upload pdf files
@app.post(
    "/upload-pdf",
    summary="Upload a PDF file",
    description="Saves the PDF, extracts its text and returns it."
)
async def upload_pdf(file: UploadFile = File(...)):

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
        #temp save patth
        save_path = f"uploads/{file.filename}"
        
        with open(save_path, "wb") as f:
                f.write(await file.read())

        cleaned_text = extract_clean_text(save_path)
        chunks = chunk_text(cleaned_text)
        
        return  {
                "message": "PDF uploaded successfully", 
                "path": save_path,
                "text": cleaned_text,
                "chunks": chunks
                }



@app.get("/")
def home():
    return {"message", "API is Working"} 