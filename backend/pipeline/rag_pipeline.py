from services.embedding_service import embed_chunks
from services.qdrant_service import search_similar
from services.rag_service import answer_question

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

    # 3) Generate final answer using GPT
    answer = answer_question(question, context_chunks)

    return {
        "question": question,
        "answer": answer,
        "context_used": context_chunks
    }
