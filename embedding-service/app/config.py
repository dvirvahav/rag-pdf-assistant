import os

# Path where File Service stores files
# Using absolute path for Docker shared volume mount
STORAGE_PATH = "/app/storage/uploads"

# Qdrant settings
QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333

COLLECTION_NAME = "pdf_chunks"

# RabbitMQ settings for audit logging
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "audit_events")
