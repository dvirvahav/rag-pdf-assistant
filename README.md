# RAG PDF Assistant

<img width="2026" height="1019" alt="image" src="https://github.com/user-attachments/assets/68ff25ab-98ba-47ed-89e8-34ccba3ec8bd" />

A RAG-based PDF assistant that lets users upload PDFs and ask questions about them using vector search and GPT. Built with a microservices architecture using FastAPI, React, and Docker.

---

## Features

- 📄 **PDF Upload** - Drag & drop or click to upload
- ⚡ **Parallel Processing** - Fast extraction for large PDFs (500+ pages)
- 🔍 **Vector Search** - Semantic search using Qdrant
- 🤖 **GPT Answers** - Accurate RAG-based responses
- 💬 **ChatGPT-style UI** - Full-screen chat interface
- 📁 **File Selector** - Switch between uploaded PDFs
- 📊 **Audit Logging** - Track all events in PostgreSQL

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                                │
│                         localhost:3000                                  │
└─────────────────────────────────────────────────────────────────────────┘
                │                                    │
                ▼                                    ▼
┌──────────────────────────┐              ┌──────────────────────────┐
│     FILE SERVICE         │              │      RAG SERVICE         │
│     localhost:8000       │              │      localhost:8002      │
└──────────────────────────┘              └──────────────────────────┘
         │         │                                  │
         ▼         ▼                                  ▼
┌─────────────┐  ┌─────────────┐              ┌─────────────┐
│   REDIS     │  │  RABBITMQ   │              │   QDRANT    │
└─────────────┘  └─────────────┘              └─────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        EMBEDDING SERVICE                                  │
│                        localhost:8001                                     │
└──────────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────┐              ┌──────────────────────────┐
│    AUDIT SERVICE         │──────────────▶      POSTGRES            │
└──────────────────────────┘              └──────────────────────────┘
```

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 3000 | React UI with ChatGPT-style interface |
| **File Service** | 8000 | PDF upload, job tracking |
| **Embedding Service** | 8001 | PDF processing pipeline |
| **RAG Service** | 8002 | Question answering |
| **Audit Service** | 8003 | Event logging |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key

### 1. Clone the repository
```bash
git clone https://github.com/dvirvahav/rag-pdf-assistant.git
cd rag-pdf-assistant
```

### 2. Set environment variables
Create `.env` file in root:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Start all services
```bash
docker-compose up -d
```

### 4. Open the app
Navigate to [http://localhost:3000](http://localhost:3000)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Required. Your OpenAI API key |
| `MAX_EXTRACTION_WORKERS` | 8 | Parallel page extraction workers |
| `MAX_EMBEDDING_WORKERS` | 4 | Parallel embedding batch workers |
| `EMBEDDING_BATCH_SIZE` | 100 | Chunks per embedding API call |

---

## API Endpoints

### File Service (8000)
```
POST /files/upload          # Upload PDF
GET  /files/jobs/{id}/status # Get job status
GET  /files/                 # List files
DELETE /files/{filename}     # Delete file
```

### RAG Service (8002)
```
POST /rag/ask               # Ask question
     Body: { "filename": "doc.pdf", "question": "What is...?" }
```

---

## Project Structure

```
rag-pdf-assistant/
├── frontend/               # React frontend
│   └── src/components/     # ChatBox, UploadBox
├── file-service/           # PDF upload & job tracking
├── embedding-service/      # PDF processing pipeline
│   └── app/pipeline/       # Extract, clean, chunk, embed
├── rag-service/            # Question answering
├── audit-service/          # Event logging
├── docs/                   # Requirements & architecture
└── docker-compose.yml      # All services orchestration
```

---

## Tech Stack

### Backend
- Python 3.10
- FastAPI
- pdfplumber
- OpenAI SDK
- Qdrant Client
- Pika (RabbitMQ)
- Redis

### Frontend
- React 18
- TypeScript
- Tailwind CSS

### Infrastructure
- Docker & Docker Compose
- Qdrant (Vector DB)
- RabbitMQ (Message Queue)
- Redis (Cache)
- PostgreSQL (Audit Logs)

---

## Development

### Run frontend locally
```bash
cd frontend
npm install
npm start
```

### Run a service locally
```bash
cd file-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## License

MIT
