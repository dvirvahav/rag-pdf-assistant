from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

# ---------------------------------------------------------
# Connect to Qdrant (Docker/local)
# ---------------------------------------------------------
client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "pdf_chunks"


# ---------------------------------------------------------
# Create collection if missing
# ---------------------------------------------------------
def init_collection(vector_size: int = 1536):
    """
    Create the collection if it does not exist yet.
    """
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        print(f"Created Qdrant collection: {COLLECTION_NAME}")
    else:
        print(f"Qdrant collection already exists: {COLLECTION_NAME}")


# ---------------------------------------------------------
# Check if a file was already indexed
# ---------------------------------------------------------
def is_file_indexed(filename: str) -> bool:
    """
    Check if at least one vector with payload.source == filename exists.
    """
    search_filter = Filter(
        must=[
            FieldCondition(
                key="source",
                match=MatchValue(value=filename)
            )
        ]
    )

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=search_filter,
        limit=1
    )

    return len(points) > 0


# ---------------------------------------------------------
# Insert embeddings + metadata
# ---------------------------------------------------------
def upsert_chunks(vectors: list, chunks: list, filename: str):
    """
    Save embeddings + their chunk text inside Qdrant.
    """
    points = []

    for i, (vector, text) in enumerate(zip(vectors, chunks)):
        point = PointStruct(
            id=f"{filename}_{i}",
            vector=vector,  # ← must be list[float]
            payload={
                "text": text,
                "source": filename,
                "chunk_id": i
            }
        )
        points.append(point)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


# ---------------------------------------------------------
# RAG Retrieval — search most similar chunks
# ---------------------------------------------------------
def search_similar(query_vector: list, top_k: int = 5):
    """
    Retrieve the top-k most similar chunks using Qdrant's new query API.
    """
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,   # ← FIXED
        limit=top_k
    )

    return results.points  # ← FIXED
