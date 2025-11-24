סבבה, הנה **README נקי ומתוקן** בלי שום בריחה, בלי קוד שחתוך, בדיוק כמו שצריך:

---

# **rag-pdf-assistant**

A simple RAG-based PDF assistant that lets users upload a PDF, extract its text, convert it into vector embeddings, store them in Qdrant, and ask questions with accurate answers based on the document’s content.

## **Features**

* Upload PDF files
* Extract and clean text
* Split text into chunks
* Generate embeddings using OpenAI
* Store vectors in Qdrant
* Ask questions and receive RAG-based answers
* Simple React UI (upload + chat)

## **Tech Stack**

**Frontend:**

* React
* Axios

**Backend:**

* Python
* FastAPI
* pdfplumber / PyPDF2
* OpenAI API
* Qdrant (Vector DB)

## **Project Structure**

```
backend/
  main.py
  services/
  qdrant/
  uploads/

frontend/
  src/
    components/
    api/
```

## **License**

MIT

---

אם תרצה, אוסיף גם **Installation + Running Instructions**.
