import os

# Base directory where uploaded files are stored.
# Using absolute path for Docker volume mount
STORAGE_PATH = "/app/storage/uploads"

# Ensure folder exists at startup
os.makedirs(STORAGE_PATH, exist_ok=True)

# RabbitMQ settings for publishing file upload events
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
EMBEDDING_QUEUE = os.getenv("EMBEDDING_QUEUE", "embedding_tasks")

# Redis settings for job status tracking
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
JOB_STATUS_TTL = int(os.getenv("JOB_STATUS_TTL", "86400"))  # 24 hours in seconds
