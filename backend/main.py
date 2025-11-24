from fastapi import FastAPI
from fastapi import UploadFile, File
from fastapi import HTTPException
import pdfplumber

app = FastAPI();



#define async function to upload pdf files
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
        #temp save patth
        save_path = f"uploads/{file.filename}"
        
        with open(save_path, "wb") as f:
              f.write(await file.read())

        extracted_text = extract_text_from_pdf(save_path)

        return  {
                "message": "PDF uploaded successfully", 
                "path": save_path,
                "text": extracted_text
                }


def extract_text_from_pdf(path: str) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
               for page in pdf.pages:
                      text += page.extract_text() or ""
        return text

@app.get("/")
def home():
    return {"message", "API is Working"} 