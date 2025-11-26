from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def is_file_indexed(filename: str) -> bool:
    flt = models.Filter(
        must=[
            models.FieldCondition(
                key="filename",
                match=models.MatchValue(value=filename)
            )
        ]
    )

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=flt,
        limit=1
    )

    return len(points) > 0


def search_similar(filename: str, query_vector: list[float], top_k: int = 5):
    flt = models.Filter(
        must=[
            models.FieldCondition(
                key="filename",
                match=models.MatchValue(value=filename)
            )
        ]
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=flt,
        limit=top_k
    )

    return results.points  # כאן יש payload["text"]
