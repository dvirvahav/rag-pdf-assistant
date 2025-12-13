# Project Requirements – rag-pdf-assistant

## 1. Goal
Build a simple RAG-based system that allows a user to upload a PDF and ask questions about it using vector search and an LLM.

---

## 2. Functional Requirements

### 2.1 PDF Upload
- User uploads a PDF from the React UI.
- Backend saves the file temporarily in `/uploads`.
- After processing, the file may be deleted (MVP).

### 2.2 Enhanced Text Extraction
- **Smart Dual-Mode Processing**: Backend first attempts text extraction using pdfplumber
- **OCR Fallback**: If text extraction yields <100 characters or appears garbled, automatically falls back to Tesseract OCR
- **Page-by-Page Processing**: Processes each page individually with detailed error tracking
- **Layout Analysis**: Detects multi-column layouts and reorders text for proper reading flow
- **Header/Footer Filtering**: Identifies and removes repeating header/footer patterns across pages
- **Error Resilience**: Continues processing despite partial page failures, logs detailed error information
- **Advanced Cleaning**: Preserves important short content (footnotes, captions, numeric values) while removing noise

### 2.3 Chunking
- Split extracted text into chunks (e.g., 500–1000 chars).
- Add overlap between chunks (e.g., 100 chars).

### 2.4 Embeddings
- For each chunk:
  - Send text to OpenAI Embeddings model.
  - Receive vector representation.

### 2.5 Vector Storage (Qdrant)
- Store embeddings, chunk text, metadata (PDF name, index).
- Use Qdrant local instance.
- Enable similarity search by cosine distance.

### 2.6 Question Answering (RAG)
- User enters a question.
- Backend:
  - Converts question → embedding.
  - Searches in Qdrant for top-k similar chunks.
  - Combines retrieved text into a prompt.
  - Asks OpenAI LLM for final answer.
- Return final answer to UI.

### 2.7 Frontend UI
- Drag & Drop PDF upload.
- Input field to ask questions.
- Chat-like response display.

---

## 3. Non-Functional Requirements
- Local processing only (no S3 required for MVP).
- Response time for query < 3 seconds (small PDFs).
- Code should be simple and minimal (MVP).
- No authentication required.

---

## 4. Tech Stack (Detailed)

### Backend
- Python 3
- FastAPI (API)
- pdfplumber / PyPDF2 (PDF text extraction)
- pytesseract + Pillow (OCR processing for scanned PDFs)
- OpenAI SDK (embeddings + LLM)
- Qdrant (vector database)
- Uvicorn (server)

### Frontend
- React
- Axios
- HTML5 Drag & Drop

---

## 5. Future Extensions (Optional)
- Multi-PDF support.
- User accounts + multi-tenancy.
- Saving full PDFs to cloud (S3).
- Processing Word/Images.
- Summaries + document insights.
