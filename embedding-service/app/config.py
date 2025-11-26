import os

# Path where File Service stores files
# Using absolute path for Docker shared volume mount
STORAGE_PATH = "/app/storage/uploads"

# Qdrant settings
QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333

COLLECTION_NAME = "pdf_chunks"
