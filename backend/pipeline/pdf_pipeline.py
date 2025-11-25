from services.file_service import save_pdf
from services.extraction_service import extract_text_from_pdf
from services.cleaning_service import clean_text
from services.chunk_service import chunk_text
from services.embedding_service import embed_chunks
from services.qdrant_service import (
    init_collection,
    is_file_indexed,
    upsert_chunks
)


def process_pdf_upload(file) -> dict:
    """
    Full PDF processing pipeline:
    1. Save file
    2. Check if indexed
    3. Extract text
    4. Clean text
    5. Chunk text
    6. Embed chunks
    7. Store in Qdrant

    Returns a structured result for the API.
    """
    print(">>> PDF PIPELINE STARTED <<<")   # debug 1

    # Check that collectino exist if not - create one
    init_collection()

    # 1) Save file
    filepath = save_pdf(file)
    filename = file.filename

    # 2) Skip if already processed
    if is_file_indexed(filename):
        return {
            "status": "already_indexed",
            "filename": filename
        }

    # 3) Extract
    raw_text = extract_text_from_pdf(filepath)

    # 4) Clean
    cleaned_text = clean_text(raw_text)

    # 5) Chunk
    chunks = chunk_text(cleaned_text)

    # 6) Embed
    vectors = embed_chunks(chunks)
    # ---- DEBUG ----
    print("\n### DEBUG BEFORE UPSERT ###")
    print("Total chunks:", len(chunks))
    print("Total vectors:", len(vectors))

    print("\nFirst chunk text (clean):")
    print(chunks[0][:200])
    print("Type:", type(chunks[0]))

    print("\nFirst vector sample:")
    print(vectors[0][:5])
    print("Type:", type(vectors[0]))
    print("### END DEBUG ###\n")
    # 7) Save in Qdrant
    upsert_chunks(vectors, chunks, filename)

    return {
        "status": "indexed",
        "filename": filename,
        "chunks_count": len(chunks)
    }
