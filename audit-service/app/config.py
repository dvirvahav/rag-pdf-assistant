import os

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "audit_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "audit_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "audit_password")

# SQLAlchemy Database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "audit_events")
