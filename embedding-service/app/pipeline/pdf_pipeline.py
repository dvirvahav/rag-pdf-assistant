import os
from app.config import STORAGE_PATH
from app.pipeline.extraction_service import extract_text_from_pdf
from app.pipeline.cleaning_service import clean_text
from app.pipeline.chunk_service import chunk_text
from app.pipeline.embedding_service import embed_chunks
from app.pipeline.qdrant_service import store_vectors, init_collection

def process_file(filename: str):
    """
    Full processing pipeline:
    1. Load file
    2. Extract text
    3. Clean text
    4. Chunk text
    5. Embed chunks
    6. Store vectors in Qdrant
    """
    init_collection()

    filepath = os.path.join(STORAGE_PATH, filename)
    if not os.path.exists(filepath):
        return {"error": "file_not_found", "filename": filename}

    # 1) extract
    text = extract_text_from_pdf(filepath)

    # 2) clean
    cleaned = clean_text(text)

    # 3) chunk
    chunks = chunk_text(cleaned)

    # 4) embed
    vectors = embed_chunks(chunks, filename)

    # 5) store
    store_vectors(vectors)

    return {
        "status": "indexed",
        "filename": filename,
        "chunks_count": len(chunks)
    }
