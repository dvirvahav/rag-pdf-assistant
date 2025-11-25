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
# Connect to local Qdrant instance (Docker or local install)
# ---------------------------------------------------------
client = QdrantClient(host="localhost", port=6333)

# Name of the collection to store vectors
COLLECTION_NAME = "pdf_chunks"


# ---------------------------------------------------------
# Initialize collection (create it if missing)
# ---------------------------------------------------------
def init_collection(vector_size: int = 1536):
    """
    Create the Qdrant collection if it does not exist.
    Stores text chunks as vectors + metadata.
    """
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )


# ---------------------------------------------------------
# Check whether a PDF file was already processed
# ---------------------------------------------------------
def is_file_indexed(filename: str) -> bool:
    """
    Check if at least one record exists with payload.source == filename.
    If yes — the file has already been indexed and should not be processed again.
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
# Save embeddings + text chunks in Qdrant
# ---------------------------------------------------------
def upsert_chunks(vectors: list, chunks: list, filename: str):
    """
    Save chunk embeddings and their text as Qdrant points.
    """
    points = []

    for i, (vector, text) in enumerate(zip(vectors, chunks)):
        point = PointStruct(
            id=i,
            vector=vector,
            payload={
                "text": text,
                "source": filename,
            }
        )
        points.append(point)

    client.upsert(collection_name=COLLECTION_NAME, points=points)


# ---------------------------------------------------------
# Search similar chunks for a user query
# ---------------------------------------------------------
def search_similar(query_vector: list, top_k: int = 5):
    """
    Return the top-k most similar chunks based on cosine similarity.
    Used during question-answering (RAG retrieval step).
    """
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )

    return results
