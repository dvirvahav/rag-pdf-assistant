from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.audit_routes import router as audit_router
from app.services.postgres_service import init_db
from app.services.rabbitmq_consumer import consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize database and start RabbitMQ consumer
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")
    
    print("Starting RabbitMQ consumer...")
    consumer.start()
    
    yield
    
    # Shutdown: Stop RabbitMQ consumer
    print("Stopping RabbitMQ consumer...")
    consumer.stop()
    print("Audit service shutdown complete")


# Application entrypoint for the Audit Service.
# Consumes audit events from RabbitMQ and stores them in PostgreSQL.
# Also exposes REST endpoints for querying audit events.
app = FastAPI(
    title="Audit Service",
    description="Consumes audit events from RabbitMQ and stores them in PostgreSQL. Provides REST API for querying audit logs.",
    version="1.0.0",
    lifespan=lifespan
)

# Register audit-related routes
app.include_router(audit_router)


@app.get("/")
def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "audit-service",
        "version": "1.0.0",
        "description": "Audit event logging service"
    }
