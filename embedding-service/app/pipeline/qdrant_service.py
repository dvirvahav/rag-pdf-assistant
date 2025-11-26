from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def init_collection():
    """
    Create the collection if it does not exist.
    Do NOT recreate it, otherwise all data is lost.
    """
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=1536,
                distance=models.Distance.COSINE
            )
        )

def store_vectors(vectors: list[dict]):
    """
    Insert batch vectors into Qdrant.
    Each dict:
    {
        "id": str,
        "embedding": [...],
        "metadata": {...}
    }
    """
    points = [
        models.PointStruct(
            id=v["id"],
            vector=v["embedding"],
            payload=v["metadata"]
        )
        for v in vectors
    ]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
