# Project Requirements – rag-pdf-assistant

## 1. Goal
Build a RAG-based system that allows users to upload PDFs and ask questions about them using vector search and an LLM. The system uses a microservices architecture with message queues for async processing.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                                │
│                         localhost:3000                                  │
│  • ChatGPT-style interface                                             │
│  • Drag & drop PDF upload                                              │
│  • File selector (localStorage)                                        │
│  • Real-time status polling                                            │
└─────────────────────────────────────────────────────────────────────────┘
                │                                    │
                ▼                                    ▼
┌──────────────────────────┐              ┌──────────────────────────┐
│     FILE SERVICE         │              │      RAG SERVICE         │
│     localhost:8000       │              │      localhost:8002      │
│  • Upload PDF            │              │  • Question answering    │
│  • Job status tracking   │              │  • Vector search         │
│  • Redis integration     │              │  • GPT integration       │
└──────────────────────────┘              └──────────────────────────┘
         │         │                                  │
         ▼         ▼                                  ▼
┌─────────────┐  ┌─────────────┐              ┌─────────────┐
│   REDIS     │  │  RABBITMQ   │              │   QDRANT    │
│   :6379     │  │   :5672     │              │   :6333     │
└─────────────┘  └─────────────┘              └─────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        EMBEDDING SERVICE                                  │
│                        localhost:8001                                     │
│  • PDF extraction (parallel)                                             │
│  • Text cleaning & chunking                                              │
│  • Batch embedding (parallel)                                            │
│  • Qdrant storage                                                        │
└──────────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────┐              ┌──────────────────────────┐
│    AUDIT SERVICE         │──────────────▶      POSTGRES            │
│    localhost:8003        │              │      :5432               │
│  • Event logging         │              │  • Audit logs storage    │
└──────────────────────────┘              └──────────────────────────┘
```

---

## 3. Functional Requirements

### 3.1 PDF Upload (File Service)
- User uploads PDF via drag & drop or file picker
- File saved to shared storage volume
- Generates unique job_id (UUID)
- Sets initial status "processing" in Redis
- Publishes task to RabbitMQ for async processing
- Returns job_id for status polling

### 3.2 Job Status Tracking
- Frontend polls `/files/jobs/{job_id}/status`
- Status values: `processing`, `completed`, `failed`
- Status stored in Redis with 24-hour TTL
- Returns chunk count on completion

### 3.3 PDF Processing Pipeline (Embedding Service)
1. **Extract** - Parallel page extraction (configurable workers)
2. **Clean** - Remove extra whitespace, normalize text
3. **Chunk** - Split into 800-char chunks with 100-char overlap
4. **Embed** - Batch embedding with parallel execution (100 chunks/batch)
5. **Store** - Upsert vectors to Qdrant

### 3.4 Error Handling
- Corrupted pages are skipped, not crash the process
- Failed pages logged to audit service
- Partial success tracking (total/failed/success pages)

### 3.5 Question Answering (RAG Service)
- User enters question in chat
- Question embedded via OpenAI
- Top-k similar chunks retrieved from Qdrant
- Context + question sent to GPT
- Answer returned to frontend

### 3.6 Frontend UI
- Full-screen ChatGPT-style interface
- Auto-expanding textarea for long questions
- File selector dropdown (persisted in localStorage)
- PDF attachment card with status indicator
- Loading dots animation while processing
- Drag & drop overlay

### 3.7 Audit Logging
- All events published to RabbitMQ
- Audit service consumes and stores in PostgreSQL
- Event types:
  - `FILE_UPLOADED`
  - `PAGE_EXTRACTION_FAILED`
  - `EXTRACTION_PARTIAL_SUCCESS`
  - `EXTRACTION_FAILED`
  - `EMBEDDING_FAILED`
  - `STORAGE_FAILED`

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Parallel PDF extraction (8 workers default)
- Parallel embedding batches (4 workers default)
- Batch size: 100 chunks per API call
- Target: 500-page PDF in ~1-2 minutes

### 4.2 Scalability
- Microservices can be scaled independently
- Message queue decouples upload from processing
- Stateless services (state in Redis/Qdrant/Postgres)

### 4.3 Reliability
- Graceful error handling for corrupted PDFs
- Audit trail for debugging
- Job status persistence in Redis

### 4.4 Configuration
- All settings via environment variables
- Configurable worker counts
- Configurable batch sizes

---

## 5. Tech Stack

### Backend Services
| Service | Tech | Purpose |
|---------|------|---------|
| File Service | FastAPI, Python | Upload, job tracking |
| Embedding Service | FastAPI, Python | PDF processing pipeline |
| RAG Service | FastAPI, Python | Question answering |
| Audit Service | FastAPI, Python | Event logging |

### Infrastructure
| Component | Tech | Purpose |
|-----------|------|---------|
| Vector DB | Qdrant | Embedding storage & search |
| Message Queue | RabbitMQ | Async task processing |
| Cache | Redis | Job status tracking |
| Database | PostgreSQL | Audit logs |

### Frontend
| Tech | Purpose |
|------|---------|
| React | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Nginx | Production serving |

### Libraries
| Library | Purpose |
|---------|---------|
| pdfplumber | PDF text extraction |
| OpenAI SDK | Embeddings + LLM |
| pika | RabbitMQ client |
| redis-py | Redis client |
| qdrant-client | Vector DB client |

---

## 6. Environment Variables

### Embedding Service
```bash
MAX_EXTRACTION_WORKERS=8    # Parallel page extraction
MAX_EMBEDDING_WORKERS=4     # Parallel embedding batches
EMBEDDING_BATCH_SIZE=100    # Chunks per API call
```

### All Services
```bash
RABBITMQ_HOST=rabbitmq
REDIS_HOST=redis
QDRANT_HOST=qdrant
OPENAI_API_KEY=sk-...
```

---

## 7. API Endpoints

### File Service (8000)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/files/upload` | Upload PDF, returns job_id |
| GET | `/files/jobs/{job_id}/status` | Get job status |
| GET | `/files/` | List all files |
| DELETE | `/files/{filename}` | Delete file |

### RAG Service (8002)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rag/ask` | Ask question about PDF |

### Embedding Service (8001)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/embed/{filename}` | Manually trigger embedding |

### Audit Service (8003)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/audit/events` | Get audit events |

---

## 8. Future Extensions
- [ ] Multi-user support with authentication
- [ ] Cloud storage (S3) for PDFs
- [ ] Streaming responses from LLM
- [ ] Support for Word/Images
- [ ] Document summaries & insights
- [ ] Conversation history persistence
- [ ] Rate limiting & quotas
