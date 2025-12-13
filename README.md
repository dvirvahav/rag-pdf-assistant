# 📄 RAG PDF Assistant

A production-ready RAG (Retrieval-Augmented Generation) system that allows users to upload PDF documents, extract and index their content using vector embeddings, and ask questions with accurate, context-aware answers powered by OpenAI's GPT models.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

### Core Functionality
- 📤 **PDF Upload & Processing** - Upload PDFs with automatic text extraction and indexing
- 🔍 **Vector Search** - Semantic search using OpenAI embeddings and Qdrant vector database
- 💬 **RAG Question Answering** - Context-aware answers using GPT-4o-mini
- 📊 **Interactive API Documentation** - Built-in Swagger UI at `/docs`

### Advanced PDF Processing
- 🤖 **OCR Integration** - Automatic OCR fallback for scanned PDFs using Tesseract
- 📄 **Layout Analysis** - Multi-column detection and text reordering
- 🎯 **Smart Cleaning** - Header/footer filtering with pattern recognition
- 🔧 **Error Resilience** - Continue processing despite partial failures
- 📏 **Intelligent Chunking** - Document-structure aware text splitting

### Technical Features
- ✅ **Comprehensive Error Handling** - Robust validation and error messages
- ✅ **Pydantic Validation** - Type-safe request/response models
- ✅ **Docker Deployment** - One-command setup with Docker Compose
- ✅ **Organized Architecture** - Services structured by domain for easy scaling
- ✅ **Hot Reload** - Development mode with automatic code reloading
- ✅ **Centralized Configuration** - Environment-based settings management

---

## 🚀 Quick Start (Docker)

### Prerequisites
- Docker Desktop installed
- OpenAI API key

### Setup & Run

```bash
# 1. Clone the repository
git clone https://github.com/dvirvahav/rag-pdf-assistant.git
cd rag-pdf-assistant

# 2. Create .env file
cp .env.example .env
# Edit .env and add your OpenAI API key:
# MY_OPENAI_KEY=sk-your-actual-openai-key-here

# 3. Start all services
docker-compose up --build

# 4. Access the API
# Swagger UI: http://localhost:8000/docs
# API: http://localhost:8000
# Qdrant Dashboard: http://localhost:6333/dashboard
```

That's it! Your RAG PDF Assistant is now running. 🎉

---

## 📚 API Documentation

### Interactive Documentation
Once running, access the interactive Swagger UI:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Available Endpoints

#### Health Check
```http
GET /
GET /health
```

#### Document Management
```http
POST /documents/upload
```
Upload a PDF file for processing and indexing.

**Request:**
- `file`: PDF file (multipart/form-data)
- Max size: 10MB
- Supported format: PDF only

**Response:**
```json
{
  "status": "indexed",
  "filename": "document.pdf",
  "chunks_count": 42
}
```

#### RAG Query
```http
POST /query/ask
```
Ask questions about indexed documents.

**Request:**
```json
{
  "question": "What is the main topic of the document?"
}
```

**Response:**
```json
{
  "question": "What is the main topic of the document?",
  "answer": "The document discusses...",
  "context_used": ["chunk1", "chunk2", "..."]
}
```

---

## 🏗️ Project Structure

```
rag-pdf-assistant/
│
├── backend/                          # Backend application
│   ├── main.py                       # FastAPI app entry point
│   ├── config.py                     # Centralized configuration
│   ├── models.py                     # Pydantic request/response models
│   │
│   ├── routes/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── upload.py                 # PDF upload endpoints
│   │   └── query.py                  # RAG query endpoints
│   │
│   ├── services/                     # Business logic services
│   │   ├── document_processing/      # PDF processing
│   │   │   ├── extraction.py         # Smart text extraction with OCR
│   │   │   ├── cleaning.py           # Advanced text cleaning
│   │   │   ├── chunking.py           # Intelligent text chunking
│   │   │   ├── layout.py             # Layout analysis & header/footer filtering
│   │   │   ├── ocr.py                # OCR processing service
│   │   │   └── types.py              # Data type definitions
│   │   │
│   │   ├── embeddings/               # Embedding generation
│   │   │   └── openai_embeddings.py
│   │   │
│   │   ├── vector_store/             # Vector database
│   │   │   └── qdrant.py             # Qdrant operations
│   │   │
│   │   ├── llm/                      # LLM services
│   │   │   ├── openai_client.py      # OpenAI client
│   │   │   └── chat.py               # Chat completions
│   │   │
│   │   └── storage/                  # File storage
│   │       └── file_manager.py
│   │
│   └── pipeline/                     # Orchestration pipelines
│       ├── pdf_pipeline.py           # PDF processing workflow
│       └── rag_pipeline.py           # RAG query workflow
│
├── docs/                             # Documentation
│   └── requirements.md               # Project requirements
│
├── frontend/                         # React frontend (optional)
│
├── uploads/                          # Temporary PDF storage
│
├── .env.example                      # Environment variables template
├── .dockerignore                     # Docker ignore rules
├── docker-compose.yml                # Docker Compose configuration
├── Dockerfile                        # Backend Docker image
├── requirements.txt                  # Python dependencies
├── DOCKER_SETUP.md                   # Detailed Docker guide
└── README.md                         # This file
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.11** - Programming language
- **Pydantic** - Data validation using Python type annotations
- **OpenAI API** - Embeddings (text-embedding-3-small) and Chat (GPT-4o-mini)
- **Qdrant** - Vector database for similarity search
- **pdfplumber** - PDF text extraction
- **pytesseract** - OCR processing for scanned PDFs
- **Pillow** - Image processing for OCR
- **python-dotenv** - Environment variable management
- **Uvicorn** - ASGI server

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

### Frontend (Optional)
- **React** - UI framework
- **Axios** - HTTP client

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Key (Required)
MY_OPENAI_KEY=sk-your-actual-openai-key-here

# API Settings (Optional)
API_HOST=0.0.0.0
API_PORT=8000

# Qdrant Settings (Optional)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Document Processing (Optional)
MAX_FILE_SIZE_MB=10
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# RAG Settings (Optional)
TOP_K_RESULTS=5
```

### Configuration File

All settings are centralized in `backend/config.py` using Pydantic Settings:
- Automatic environment variable loading
- Type validation
- Default values
- Easy to extend

---

## 💻 Development

### Local Development (Without Docker)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Qdrant (Docker)
docker-compose up -d qdrant

# 3. Set environment variables
export MY_OPENAI_KEY=sk-your-key-here

# 4. Run the backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend
```

### Code Quality

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

---

## 🐳 Docker Commands

### Basic Commands
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend
```

### Troubleshooting
```bash
# Check service status
docker-compose ps

# Access backend container
docker-compose exec backend bash

# Clear all data and restart
docker-compose down -v
docker-compose up --build
```

For detailed Docker instructions, see [DOCKER_SETUP.md](DOCKER_SETUP.md).

---

## 📖 How It Works

### 1. Enhanced PDF Upload & Processing Pipeline

```
User uploads PDF
    ↓
Save file to /uploads
    ↓
Smart Text Extraction (pdfplumber + OCR fallback)
    ↓
Layout Analysis (multi-column detection & reordering)
    ↓
Header/Footer Filtering (pattern-based removal)
    ↓
Advanced Text Cleaning (preserve important short blocks)
    ↓
Intelligent Chunking (document-structure aware splitting)
    ↓
Generate embeddings (OpenAI)
    ↓
Store in Qdrant (vectors + metadata)
```

**Smart Processing Features:**
- **OCR Integration**: Automatic fallback to Tesseract OCR for scanned PDFs
- **Layout Intelligence**: Detects and reorders multi-column text
- **Content Preservation**: Keeps important short blocks (footnotes, captions, etc.)
- **Error Resilience**: Continues processing despite partial page failures
- **Quality Assurance**: Filters low-quality chunks and validates content

### 2. RAG Query Pipeline

```
User asks question
    ↓
Generate question embedding (OpenAI)
    ↓
Search similar chunks (Qdrant)
    ↓
Retrieve top-k relevant chunks
    ↓
Build context prompt
    ↓
Generate answer (GPT-4o-mini)
    ↓
Return answer to user
```

---

## 🔒 Security Considerations

- ✅ File upload validation (type, size, filename sanitization)
- ✅ Path traversal prevention
- ✅ Environment variable protection (.env not in git)
- ✅ Input validation with Pydantic
- ✅ Error messages don't expose sensitive info

---

## 🎨 Frontend Application

A modern, mobile-responsive React frontend is now included!

### Features
- 📱 **Mobile-First Design** - Works perfectly on all devices
- 💬 **ChatGPT-like Interface** - Familiar conversation experience
- 📄 **Drag-and-Drop Upload** - Easy PDF file selection
- ⚡ **Real-time Updates** - Live processing status
- 🎨 **Modern UI** - Clean design with Tailwind CSS

### Quick Start

```bash
# Start backend (Docker)
docker-compose up

# Start frontend (separate terminal)
cd frontend
npm install
npm run dev

# Access the app
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
```

See [frontend/README.md](frontend/README.md) for detailed setup instructions.

---

## ☁️ AWS Production Deployment

Complete CI/CD setup for production deployment on AWS!

### Architecture
- **Frontend**: React app → S3 + CloudFront (CDN)
- **Backend**: Docker containers → EC2 + ECR
- **CI/CD**: GitHub Actions for automated deployment

### Quick Deploy

1. **Set up AWS resources:**
   - S3 bucket for frontend
   - CloudFront distribution
   - EC2 instance for backend
   - ECR repository

2. **Configure GitHub Secrets:**
   ```bash
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket
   CLOUDFRONT_DISTRIBUTION_ID=your-dist-id
   ECR_REGISTRY=your-registry
   EC2_HOST=your-ec2-ip
   EC2_USER=ubuntu
   VITE_API_URL=https://api.yourdomain.com
   ```

3. **Deploy automatically:**
   - Push to `main` branch
   - GitHub Actions deploys frontend & backend
   - Access your live app!

See deployment guides in the docs folder.

---

## 🚧 Future Enhancements

- [x] Frontend React application
- [x] Mobile-responsive design
- [x] AWS production deployment
- [x] GitHub Actions CI/CD
- [ ] Multi-PDF support with document management
- [ ] User authentication and authorization
- [ ] Conversation history and context
- [ ] Support for Word documents and images
- [ ] Document summaries and insights
- [ ] Enhanced monitoring and logging

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [OpenAI](https://openai.com/) - Embeddings and LLM
- [Qdrant](https://qdrant.tech/) - Vector database
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF processing

---

**Built with ❤️ using FastAPI, OpenAI, and Qdrant**
