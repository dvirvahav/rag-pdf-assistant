import os
import traceback
from app.config import STORAGE_PATH
from app.pipeline.extraction_service import extract_text_from_pdf
from app.pipeline.cleaning_service import clean_text
from app.pipeline.chunk_service import chunk_text
from app.pipeline.embedding_service import embed_chunks
from app.pipeline.qdrant_service import store_vectors, init_collection
from app.services.audit_publisher import publish_audit_event


def process_file(filename: str):
    """
    Full processing pipeline:
    1. Load file
    2. Extract text
    3. Clean text
    4. Chunk text
    5. Embed chunks
    6. Store vectors in Qdrant

    On failure at any step, an audit event is published to RabbitMQ.
    """
    try:
        init_collection()
    except Exception as e:
        publish_audit_event("COLLECTION_INIT_FAILED", {
            "filename": filename,
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        return {"error": "collection_init_failed", "filename": filename, "details": str(e)}

    filepath = os.path.join(STORAGE_PATH, filename)
    if not os.path.exists(filepath):
        publish_audit_event("FILE_NOT_FOUND", {
            "filename": filename,
            "filepath": filepath
        })
        return {"error": "file_not_found", "filename": filename}

    # 1) Extract text from PDF
    try:
        text = extract_text_from_pdf(filepath, filename)
    except Exception as e:
        publish_audit_event("EXTRACTION_FAILED", {
            "filename": filename,
            "step": "extract_text_from_pdf",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        return {"error": "extraction_failed", "filename": filename, "details": str(e)}

    # 2) Clean text
    try:
        cleaned = clean_text(text)
    except Exception as e:
        publish_audit_event("CLEANING_FAILED", {
            "filename": filename,
            "step": "clean_text",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        return {"error": "cleaning_failed", "filename": filename, "details": str(e)}

    # 3) Chunk text
    try:
        chunks = chunk_text(cleaned)
    except Exception as e:
        publish_audit_event("CHUNKING_FAILED", {
            "filename": filename,
            "step": "chunk_text",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        return {"error": "chunking_failed", "filename": filename, "details": str(e)}

    # 4) Embed chunks
    try:
        vectors = embed_chunks(chunks, filename)
    except Exception as e:
        publish_audit_event("EMBEDDING_FAILED", {
            "filename": filename,
            "step": "embed_chunks",
            "chunks_count": len(chunks),
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        return {"error": "embedding_failed", "filename": filename, "details": str(e)}

    # 5) Store vectors in Qdrant
    try:
        store_vectors(vectors)
    except Exception as e:
        publish_audit_event("STORAGE_FAILED", {
            "filename": filename,
            "step": "store_vectors",
            "vectors_count": len(vectors),
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        return {"error": "storage_failed", "filename": filename, "details": str(e)}

    return {
        "status": "indexed",
        "filename": filename,
        "chunks_count": len(chunks)
    }
