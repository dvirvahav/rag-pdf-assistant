from enum import Enum


class EventType(str, Enum):
    """
    Enumeration of all audit event types across the RAG PDF Assistant system.

    This enum provides type safety and a single source of truth for event types
    used across all microservices.
    """

    # File Service Events
    FILE_UPLOADED = "FILE_UPLOADED"
    FILE_PROCESSED = "FILE_PROCESSED"

    # Embedding Service Events
    EMBEDDING_CREATED = "EMBEDDING_CREATED"
    EMBEDDING_FAILED = "EMBEDDING_FAILED"
    COLLECTION_INIT_FAILED = "COLLECTION_INIT_FAILED"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    CLEANING_FAILED = "CLEANING_FAILED"
    CHUNKING_FAILED = "CHUNKING_FAILED"
    STORAGE_FAILED = "STORAGE_FAILED"

    # RAG Service Events
    RAG_QUERY_RECEIVED = "RAG_QUERY_RECEIVED"
    RAG_RESPONSE_SENT = "RAG_RESPONSE_SENT"

    # General Service Events
    SERVICE_ERROR = "SERVICE_ERROR"
