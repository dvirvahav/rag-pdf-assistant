from backend.services.embeddings import embed_chunks
from backend.services.vector_store import search_similar
from backend.services.llm import answer_question, refine_question
from backend.services.document_processing.metadata_extractor import format_metadata_for_context
from backend.config import settings

def process_question(question: str) -> dict:
    """
    Full RAG pipeline with safe question refinement:
    1. Refine the user's question for better retrieval (with fallback)
    2. Embed the refined question
    3. Retrieve similar chunks from Qdrant
    4. Pass the context + original question to the RAG answer service
    """
    original_question = question

    # 1) Safe question refinement (never fails)
    refined_question = refine_question(question)

    # 2) Create embedding for refined question (better retrieval)
    question_vector = embed_chunks([refined_question])[0]

    # 3) Retrieve most similar chunks
    search_results = search_similar(question_vector)
    context_chunks = [r.payload["text"] for r in search_results]

    # 4) Include document metadata in context if available
    if search_results and settings.INCLUDE_DOC_METADATA:
        # Get metadata from the first result (assuming all chunks from same document)
        first_result = search_results[0]
        doc_metadata = first_result.payload.get("doc_metadata")

        if doc_metadata:
            # Format metadata for context
            metadata_context = format_metadata_for_context(doc_metadata)
            # Insert metadata at the beginning of context
            context_chunks.insert(0, metadata_context)

    # 5) Generate final answer using original question
    answer = answer_question(original_question, context_chunks)

    return {
        "question": original_question,
        "refined_question": refined_question if refined_question != original_question else None,
        "answer": answer,
        "context_used": context_chunks
    }
