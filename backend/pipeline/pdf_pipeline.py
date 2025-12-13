from backend.services.storage import save_pdf
from backend.services.document_processing import extract_text_from_pdf_smart, clean_text, chunk_text
from backend.services.embeddings import embed_chunks
from backend.services.vector_store import init_collection, is_file_indexed, upsert_chunks


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

    # 3) Extract with OCR fallback
    extraction_result = extract_text_from_pdf_smart(filepath)

    # Log extraction results
    print(f"Extraction completed: {extraction_result.successful_pages}/{extraction_result.total_pages} pages successful")
    if extraction_result.errors:
        print(f"Extraction errors: {len(extraction_result.errors)} pages failed")
        for error in extraction_result.errors[:3]:  # Show first 3 errors
            print(f"  Page {error['page_number']}: {error['error']}")

    # Check if we have any text to process
    if not extraction_result.full_text.strip():
        return {
            "status": "extraction_failed",
            "filename": filename,
            "error": "No text could be extracted from the PDF",
            "extraction_stats": extraction_result.stats
        }

    # 4) Clean
    cleaned_text = clean_text(extraction_result.full_text)

    # 5) Chunk
    chunks = chunk_text(cleaned_text)

    # 6) Embed
    vectors = embed_chunks(chunks)

    # ---- DEBUG ----
    print("\n### DEBUG BEFORE UPSERT ###")
    print("Total chunks:", len(chunks))
    print("Total vectors:", len(vectors))

    if chunks:
        print("\nFirst chunk text (clean):")
        print(chunks[0][:200])
        print("Type:", type(chunks[0]))

    if vectors:
        print("\nFirst vector sample:")
        print(vectors[0][:5])
        print("Type:", type(vectors[0]))
    print("### END DEBUG ###\n")

    # 7) Save in Qdrant
    upsert_chunks(vectors, chunks, filename)

    return {
        "status": "indexed",
        "filename": filename,
        "chunks_count": len(chunks),
        "extraction_stats": extraction_result.stats,
        "extraction_errors": len(extraction_result.errors)
    }
