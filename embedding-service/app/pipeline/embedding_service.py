import uuid
from app.services.openai_client import get_openai_client

client = get_openai_client()

def embed_chunks(chunks: list[str], filename: str) -> list[dict]:
    """
    Take chunk texts, generate embeddings, and return
    list of dicts ready for Qdrant insertion.

    Each entry:
    {
        "id": "uuid-string",
        "embedding": [...],
        "metadata": {
            "text": "...",
            "filename": "file.pdf",
            "chunk_id": 3
        }
    }
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )

    vectors = []
    for index, emb in enumerate(response.data):
        vectors.append({
            "id": str(uuid.uuid4()),
            "embedding": emb.embedding,
            "metadata": {
                "text": chunks[index],
                "filename": filename,
                "chunk_id": index
            }
        })

    return vectors
