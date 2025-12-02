# API Gateway Documentation

## Overview

The API Gateway serves as the single entry point for all client requests to the RAG PDF Assistant microservices. It provides centralized authentication, request routing, rate limiting, and logging.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                                │
│                         localhost:3000                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                │ All requests go through gateway
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       API GATEWAY (FastAPI)                             │
│                       localhost:8080                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ • JWT Token Validation (Keycloak)                                 │ │
│  │ • Request Routing & Proxying                                      │ │
│  │ • Rate Limiting (60 req/min per IP)                               │ │
│  │ • CORS Handling (Centralized)                                     │ │
│  │ • Request/Response Logging                                        │ │
│  │ • Correlation ID Tracking                                         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ File Service │ │ Embedding    │ │ RAG Service  │ │ Audit Service│ │ Admin Service│
│   :8000      │ │ Service      │ │   :8002      │ │   :8003      │ │   :8005      │
│ (Internal)   │ │   :8001      │ │ (Internal)   │ │ (Internal)   │ │ (Internal)   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## Features

### 1. **Centralized Authentication**
- Validates JWT tokens from Keycloak
- Extracts user information (ID, email, roles)
- Passes user context to backend services via headers
- Handles token refresh automatically

### 2. **Request Routing**
Routes frontend requests to appropriate backend services:

| Frontend Request | Routes To | Description |
|-----------------|-----------|-------------|
| `POST /api/files/upload` | file-service:8000 | Upload PDF files |
| `GET /api/files/` | file-service:8000 | List uploaded files |
| `GET /api/files/jobs/{id}/status` | file-service:8000 | Check job status |
| `DELETE /api/files/{filename}` | file-service:8000 | Delete file |
| `POST /api/rag/ask` | rag-service:8002 | Ask questions |
| `GET /api/admin/*` | admin-service:8005 | Admin operations |
| `GET /api/audit/events` | audit-service:8003 | Audit logs |

### 3. **CORS Configuration**
- Single centralized CORS policy
- Allows requests from `http://localhost:3000` (frontend)
- Exposes custom headers: `X-Correlation-ID`, `X-Process-Time`
- Backend services no longer need CORS middleware

### 4. **Rate Limiting**
- 60 requests per minute per IP address
- Prevents API abuse
- Returns 429 status code when limit exceeded

### 5. **Request Logging**
- Logs all incoming requests
- Tracks processing time
- Generates correlation IDs for request tracing
- Logs errors with context

### 6. **User Context Headers**
Gateway adds these headers to backend requests:
- `X-User-Id`: User's unique identifier
- `X-User-Email`: User's email address
- `X-User-Name`: User's username
- `X-User-Roles`: Comma-separated list of roles
- `X-Correlation-ID`: Request tracking ID

---

## Configuration

### Environment Variables

```bash
# Service Info
SERVICE_NAME=API Gateway
VERSION=1.0.0

# Keycloak Configuration
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=rag-assistant
KEYCLOAK_CLIENT_ID=rag-backend

# Backend Service URLs (Docker internal network)
FILE_SERVICE_URL=http://file-service:8000
EMBEDDING_SERVICE_URL=http://embedding-service:8001
RAG_SERVICE_URL=http://rag-service:8002
AUDIT_SERVICE_URL=http://audit-service:8003
ADMIN_SERVICE_URL=http://admin-service:8000

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
```

---

## API Endpoints

### Health Check
```
GET /health
```
Returns gateway health status.

**Response:**
```json
{
  "service": "API Gateway",
  "version": "1.0.0",
  "status": "healthy"
}
```

### Root
```
GET /
```
Returns API information.

**Response:**
```json
{
  "service": "API Gateway",
  "version": "1.0.0",
  "description": "API Gateway for RAG PDF Assistant",
  "docs": "/docs",
  "health": "/health"
}
```

### API Documentation
```
GET /docs
```
Interactive Swagger UI documentation.

---

## Security

### Authentication Flow

1. **Frontend Login**
   - User logs in via Keycloak
   - Receives JWT access token

2. **API Request**
   - Frontend includes token in `Authorization: Bearer <token>` header
   - Sends request to API Gateway

3. **Token Validation**
   - Gateway validates JWT signature using Keycloak public key
   - Checks token expiration
   - Extracts user claims (ID, email, roles)

4. **Request Forwarding**
   - Gateway adds user context headers
   - Forwards request to backend service
   - Backend trusts gateway headers (no re-validation needed)

5. **Response**
   - Backend processes request
   - Gateway returns response to frontend

### Role-Based Access Control

Admin endpoints require `admin` role:
- `/api/admin/health`
- `/api/admin/services/status`
- `/api/admin/audit/search`

Gateway checks roles before forwarding requests.

---

## Error Handling

### Common Error Responses

**401 Unauthorized**
```json
{
  "detail": "Authentication required"
}
```

**403 Forbidden**
```json
{
  "detail": "Role 'admin' required"
}
```

**429 Too Many Requests**
```json
{
  "detail": "Rate limit exceeded"
}
```

**502 Bad Gateway**
```json
{
  "detail": "Bad gateway"
}
```

**504 Gateway Timeout**
```json
{
  "detail": "Gateway timeout"
}
```

---

## Deployment

### Docker Compose

The API Gateway is included in `docker-compose.yml`:

```yaml
api-gateway:
  build:
    context: .
    dockerfile: ./api-gateway/Dockerfile
  container_name: api-gateway
  ports:
    - "8080:8080"
  environment:
    - KEYCLOAK_URL=http://keycloak:8080
    - FILE_SERVICE_URL=http://file-service:8000
    # ... other services
  depends_on:
    - keycloak
    - file-service
    - rag-service
  networks:
    - ragnet
```

### Port Changes

- **API Gateway**: `8080` (external)
- **Keycloak**: `8090` (external, changed from 8080)
- **Backend Services**: Internal only (no external exposure needed)

---

## Frontend Integration

### Before (Multiple Endpoints)
```typescript
const fileClient = axios.create({
  baseURL: 'http://localhost:8000'
});

const ragClient = axios.create({
  baseURL: 'http://localhost:8002'
});
```

### After (Single Gateway)
```typescript
const apiClient = axios.create({
  baseURL: 'http://localhost:8080'
});

// All requests go through gateway
apiClient.post('/api/files/upload', formData);
apiClient.post('/api/rag/ask', { question });
```

---

## Monitoring

### Request Tracing

Every request gets a unique `X-Correlation-ID` header:

```
[abc-123-def] POST /api/files/upload - Client: 172.18.0.1
[abc-123-def] POST /api/files/upload - Status: 200 - Time: 1.234s
```

Use correlation IDs to trace requests across services.

### Metrics

Gateway logs include:
- Request method and path
- Client IP address
- Response status code
- Processing time
- Errors with stack traces

---

## Benefits

✅ **Single Entry Point**: Frontend only needs to know one URL
✅ **Centralized Security**: Authentication logic in one place
✅ **Simplified CORS**: No CORS configuration in backend services
✅ **Rate Limiting**: Protect backend from abuse
✅ **Request Tracing**: Correlation IDs for debugging
✅ **Scalability**: Easy to add/remove backend services
✅ **Production Ready**: Standard microservices pattern

---

## Troubleshooting

### Gateway Not Starting
- Check Keycloak is running and healthy
- Verify backend services are accessible
- Check environment variables are set correctly

### 401 Unauthorized Errors
- Verify Keycloak is accessible at configured URL
- Check JWT token is valid and not expired
- Ensure Keycloak realm and client ID are correct

### 502 Bad Gateway Errors
- Check backend service is running
- Verify service URLs in environment variables
- Check Docker network connectivity

### CORS Errors
- Verify frontend URL is in `CORS_ORIGINS`
- Check browser console for specific CORS error
- Ensure credentials are included in requests

---

## Development

### Running Locally

```bash
cd api-gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Testing

```bash
# Health check
curl http://localhost:8080/health

# With authentication
curl -H "Authorization: Bearer <token>" \
     http://localhost:8080/api/files/
```

---

## Future Enhancements

- [ ] Circuit breaker pattern for resilience
- [ ] Request/response caching
- [ ] API versioning support
- [ ] Metrics export (Prometheus)
- [ ] Distributed tracing (Jaeger)
- [ ] GraphQL gateway support
