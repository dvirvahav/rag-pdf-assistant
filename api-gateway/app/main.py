"""
API Gateway - Main Application Entry Point
Centralized entry point for all microservices in the RAG PDF Assistant system.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes.proxy_routes import router as proxy_router

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title="API Gateway",
    description="Centralized API Gateway for RAG PDF Assistant microservices",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# CORS MIDDLEWARE - Centralized CORS configuration
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Process-Time"]
)

# ============================================================================
# LOGGING MIDDLEWARE - Request/Response logging
# ============================================================================
app.add_middleware(LoggingMiddleware)

# ============================================================================
# ROUTES
# ============================================================================
app.include_router(proxy_router)


# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.get("/health")
async def health_check():
    """Gateway health check endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "healthy"
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "description": "API Gateway for RAG PDF Assistant",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.VERSION}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    logger.info(f"Rate Limiting: {'Enabled' if settings.RATE_LIMIT_ENABLED else 'Disabled'}")
    logger.info("API Gateway is ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info(f"Shutting down {settings.SERVICE_NAME}")
