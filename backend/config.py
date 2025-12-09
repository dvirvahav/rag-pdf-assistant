"""
Centralized configuration for the RAG PDF Assistant backend.
All settings are loaded from environment variables.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ========================================
    # API Settings
    # ========================================
    API_TITLE: str = "📄 RAG PDF Assistant API"
    API_DESCRIPTION: str = "API for uploading PDF files, indexing them into Qdrant, and answering questions using RAG."
    API_VERSION: str = "1.3.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # ========================================
    # OpenAI Settings
    # ========================================
    MY_OPENAI_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o-mini"
    
    # ========================================
    # Qdrant Settings
    # ========================================
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "pdf_chunks"
    VECTOR_SIZE: int = 1536
    
    # ========================================
    # Document Processing Settings
    # ========================================
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    
    # ========================================
    # RAG Settings
    # ========================================
    TOP_K_RESULTS: int = 5

    # ========================================
    # Async Processing Settings
    # ========================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASSWORD: str = "admin"

    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key with fallback"""
        key = self.MY_OPENAI_KEY or self.OPENAI_API_KEY
        if not key:
            raise ValueError("OpenAI API key not found. Please set MY_OPENAI_KEY or OPENAI_API_KEY in .env file")
        return key
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def celery_broker_url(self) -> str:
        """Get Celery broker URL"""
        if self.CELERY_BROKER_URL:
            return self.CELERY_BROKER_URL
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"

    @property
    def celery_result_backend(self) -> str:
        """Get Celery result backend URL"""
        if self.CELERY_RESULT_BACKEND:
            return self.CELERY_RESULT_BACKEND
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Global settings instance
settings = Settings()
