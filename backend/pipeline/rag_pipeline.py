from backend.services.embeddings import embed_chunks
from backend.services.vector_store import search_similar
from backend.services.llm import answer_question
from backend.services.document_processing.metadata_extractor import format_metadata_for_context
from backend.config import settings

def process_question(question: str) -> dict:
    """
    Full RAG pipeline:
    1. Embed the user's question
    2. Retrieve similar chunks from Qdrant
    3. Pass the context + question to the RAG answer service
    """

    # 1) Create embedding for question
    question_vector = embed_chunks([question])[0]

    # 2) Retrieve most similar chunks
    search_results = search_similar(question_vector)
    context_chunks = [r.payload["text"] for r in search_results]

    # 3) Include document metadata in context if available
    if search_results and settings.INCLUDE_DOC_METADATA:
        # Get metadata from the first result (assuming all chunks from same document)
        first_result = search_results[0]
        doc_metadata = first_result.payload.get("doc_metadata")

        if doc_metadata:
            # Format metadata for context
            metadata_context = format_metadata_for_context(doc_metadata)
            # Insert metadata at the beginning of context
            context_chunks.insert(0, metadata_context)

    # 4) Generate final answer using GPT
    answer = answer_question(question, context_chunks)

    return {
        "question": question,
        "answer": answer,
        "context_used": context_chunks
    }
