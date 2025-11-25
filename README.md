
---

# **rag-pdf-assistant**

A simple RAG-based PDF assistant that lets users upload a PDF, extract its text, convert it into vector embeddings, store them in Qdrant, and ask questions with accurate answers based on the document’s content.
This project demonstrates a minimal end-to-end RAG system using FastAPI (Python) and React.

---

## **Features**

* Upload PDF files
* Extract and clean text
* Split text into chunks
* Generate embeddings using OpenAI
* Store vectors in Qdrant
* Retrieve relevant chunks using vector search
* Ask questions and receive accurate RAG-based answers
* Simple React UI (upload + chat)

---

## **Tech Stack**

### **Frontend**

* React
* Axios

### **Backend**

* Python
* FastAPI
* pdfplumber / PyPDF2
* OpenAI API
* Qdrant (Vector DB)

---

## **Project Structure**

```
docs/                # requirements, architecture notes
backend/
  main.py            # FastAPI entrypoint
  services/          # text extraction, chunking, embeddings
  qdrant/            # vector database interactions
  uploads/           # temporary PDF storage

frontend/
  src/
    components/      # Upload + Chat UI
    api/             # API requests
```

---

## **License**

MIT

---
