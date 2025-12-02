"""
Configuration for Admin Service.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Admin Service configuration settings.
    """
    # Service Info
    SERVICE_NAME: str = "admin-service"
    VERSION: str = "1.0.0"

    # Keycloak Configuration
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "rag-assistant")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "rag-backend")
    KEYCLOAK_CLIENT_SECRET: str = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

    # Microservices URLs
    AUDIT_SERVICE_URL: str = os.getenv("AUDIT_SERVICE_URL", "http://audit-service:8000")
    FILE_SERVICE_URL: str = os.getenv("FILE_SERVICE_URL", "http://file-service:8000")
    EMBEDDING_SERVICE_URL: str = os.getenv("EMBEDDING_SERVICE_URL", "http://embedding-service:8000")
    RAG_SERVICE_URL: str = os.getenv("RAG_SERVICE_URL", "http://rag-service:8000")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
