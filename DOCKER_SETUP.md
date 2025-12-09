# 🐳 Docker Setup Guide

## Prerequisites

- Docker Desktop installed
- Docker Compose installed (comes with Docker Desktop)
- `.env` file with your OpenAI API key

## Quick Start

### 1. Setup Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
MY_OPENAI_KEY=sk-your-actual-openai-key-here
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### 2. Build and Start All Services

```bash
docker-compose up --build
```

Or run in detached mode (background):

```bash
docker-compose up -d --build
```

### 3. Access the Application

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Docker Commands

### Start Services
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears data)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f qdrant
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Check Status
```bash
docker-compose ps
```

## Development Workflow

### Hot Reload

The backend service has hot reload enabled. Any changes to Python files in `backend/` will automatically restart the server.

### Accessing Container Shell

```bash
# Backend container
docker-compose exec backend bash

# Qdrant container
docker-compose exec qdrant sh
```

### Rebuild After Dependency Changes

If you modify `requirements.txt`:

```bash
docker-compose up --build
```

## Troubleshooting

### Port Already in Use

If port 8000 or 6333 is already in use:

1. Stop the conflicting service
2. Or modify ports in `docker-compose.yml`:
   ```yaml
   ports:
     - "8001:8000"  # Use 8001 instead of 8000
   ```

### Backend Can't Connect to Qdrant

Make sure both services are on the same network. Check `docker-compose.yml`:
- Both services should have `networks: - rag-network`
- Backend should use `QDRANT_HOST=qdrant` (service name, not localhost)

### Clear All Data

```bash
# Stop and remove everything including volumes
docker-compose down -v

# Restart fresh
docker-compose up --build
```

### View Container Logs

```bash
# Real-time logs
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

## Production Deployment

For production, modify `Dockerfile`:

1. Remove `--reload` flag from CMD
2. Use production WSGI server (gunicorn):

```dockerfile
CMD ["gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

3. Add gunicorn to `requirements.txt`:
```
gunicorn==21.2.0
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Backend    │───▶│   Qdrant     │  │
│  │  (FastAPI)   │    │  (Vector DB) │  │
│  │  Port: 8000  │    │  Port: 6333  │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │          │
└─────────┼────────────────────┼──────────┘
          │                    │
          ▼                    ▼
    Host: 8000           Host: 6333
```

## Next Steps

1. Upload a PDF: `POST http://localhost:8000/documents/upload`
2. Ask a question: `POST http://localhost:8000/query/ask`
3. Check API docs: http://localhost:8000/docs
