"""
API Gateway Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API Gateway configuration settings"""

    # Service Info
    SERVICE_NAME: str = "API Gateway"
    VERSION: str = "1.0.0"

    # Keycloak Configuration
    KEYCLOAK_URL: str = "http://keycloak:8080"
    KEYCLOAK_REALM: str = "rag-assistant"
    KEYCLOAK_CLIENT_ID: str = "rag-backend"

    # Backend Service URLs (internal Docker network)
    FILE_SERVICE_URL: str = "http://file-service:8000"
    EMBEDDING_SERVICE_URL: str = "http://embedding-service:8001"
    RAG_SERVICE_URL: str = "http://rag-service:8002"
    AUDIT_SERVICE_URL: str = "http://audit-service:8003"
    ADMIN_SERVICE_URL: str = "http://admin-service:8000"

    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
