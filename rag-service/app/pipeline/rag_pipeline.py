from app.services.openai_client import get_openai_client
from app.services.qdrant_service import search_similar
from app.services.rag_service import answer_question

client = get_openai_client()

def embed_question(question: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[question]
    )
    return response.data[0].embedding


def ask_question(filename: str, question: str):
    # 1) embed question
    question_vector = embed_question(question)

    # 2) search in Qdrant
    matches = search_similar(filename, question_vector)

    # 3) extract text from payload
    context_chunks = [
        m.payload["text"]
        for m in matches
    ]

    # 4) GPT final answer
    answer = answer_question(question, context_chunks)

    return {
        "filename": filename,
        "question": question,
        "answer": answer,
        "context_used": context_chunks
    }
