import uuid
from concurrent.futures import ThreadPoolExecutor
from app.services.openai_client import get_openai_client
from app.config import MAX_EMBEDDING_WORKERS, EMBEDDING_BATCH_SIZE

client = get_openai_client()


def embed_batch(batch_data: tuple) -> list[dict]:
    """
    Embed a single batch of chunks.

    Args:
        batch_data: Tuple of (batch_chunks, start_index, filename)

    Returns:
        list: List of vector dicts ready for Qdrant
    """
    batch_chunks, start_index, filename = batch_data

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=batch_chunks
    )

    vectors = []
    for i, emb in enumerate(response.data):
        vectors.append({
            "id": str(uuid.uuid4()),
            "embedding": emb.embedding,
            "metadata": {
                "text": batch_chunks[i],
                "filename": filename,
                "chunk_id": start_index + i
            }
        })

    return vectors


def embed_chunks(chunks: list[str], filename: str) -> list[dict]:
    """
    Take chunk texts, generate embeddings, and return
    list of dicts ready for Qdrant insertion.

    Uses batch processing and parallel execution for large chunk lists.

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
    # For small chunk lists, process in single batch
    if len(chunks) <= EMBEDDING_BATCH_SIZE:
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

    # For large chunk lists, split into batches and process in parallel
    batches = []
    for i in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch_chunks = chunks[i:i + EMBEDDING_BATCH_SIZE]
        batches.append((batch_chunks, i, filename))

    # Process batches in parallel
    all_vectors = []
    with ThreadPoolExecutor(max_workers=MAX_EMBEDDING_WORKERS) as executor:
        batch_results = list(executor.map(embed_batch, batches))

    # Flatten results
    for batch_vectors in batch_results:
        all_vectors.extend(batch_vectors)

    return all_vectors
