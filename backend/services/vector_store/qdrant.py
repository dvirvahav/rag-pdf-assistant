from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from qdrant_client.http.exceptions import UnexpectedResponse, ResponseHandlingException
import logging
import hashlib

from backend.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Connect to Qdrant (Docker/local)
# ---------------------------------------------------------
try:
    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    logger.info(f"Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
except Exception as e:
    logger.error(f"Failed to initialize Qdrant client: {e}")
    raise ConnectionError(f"Cannot connect to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}. Is Qdrant running? Error: {str(e)}")

COLLECTION_NAME = "pdf_chunks"


# ---------------------------------------------------------
# Create collection if missing
# ---------------------------------------------------------
def init_collection(vector_size: int = 1536):
    """
    Create the collection if it does not exist yet.
    
    Args:
        vector_size (int): Size of the embedding vectors
        
    Raises:
        ConnectionError: If cannot connect to Qdrant
        RuntimeError: If collection creation fails
    """
    try:
        if not client.collection_exists(COLLECTION_NAME):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        else:
            logger.info(f"Qdrant collection already exists: {COLLECTION_NAME}")
            
    except UnexpectedResponse as e:
        raise ConnectionError(f"Qdrant connection error: {str(e)}")
    except ResponseHandlingException as e:
        raise RuntimeError(f"Qdrant response handling error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Qdrant collection: {str(e)}")


# ---------------------------------------------------------
# Check if a file was already indexed
# ---------------------------------------------------------
def is_file_indexed(filename: str) -> bool:
    """
    Check if at least one vector with payload.source == filename exists.
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if file is indexed, False otherwise
        
    Raises:
        ValueError: If filename is invalid
        RuntimeError: If Qdrant query fails
    """
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")
    
    try:
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
        
    except UnexpectedResponse as e:
        raise RuntimeError(f"Qdrant query failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to check if file is indexed: {str(e)}")


# ---------------------------------------------------------
# Insert embeddings + metadata
# ---------------------------------------------------------
def upsert_chunks(vectors: list, chunks: list, filename: str):
    """
    Save embeddings + their chunk text inside Qdrant.
    
    Args:
        vectors (list): List of embedding vectors
        chunks (list): List of text chunks
        filename (str): Source filename
        
    Raises:
        ValueError: If inputs are invalid
        RuntimeError: If upsert operation fails
    """
    if not vectors or not chunks:
        raise ValueError("Vectors and chunks cannot be empty")
    
    if len(vectors) != len(chunks):
        raise ValueError(f"Vectors and chunks must have same length. Got {len(vectors)} vectors and {len(chunks)} chunks")
    
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")
    
    try:
        points = []

        for i, (vector, text) in enumerate(zip(vectors, chunks)):
            # Validate vector
            if not isinstance(vector, list) or not vector:
                raise ValueError(f"Vector at index {i} is invalid")

            # Generate valid point ID using hash (handles special characters)
            point_id = hashlib.md5(f"{filename}_{i}".encode('utf-8')).hexdigest()

            point = PointStruct(
                id=point_id,
                vector=vector,
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
        
        logger.info(f"Successfully upserted {len(points)} chunks for file: {filename}")
        
    except UnexpectedResponse as e:
        raise RuntimeError(f"Qdrant upsert failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to upsert chunks: {str(e)}")


# ---------------------------------------------------------
# RAG Retrieval — search most similar chunks
# ---------------------------------------------------------
def search_similar(query_vector: list, top_k: int = 5):
    """
    Retrieve the top-k most similar chunks using Qdrant's query API.
    
    Args:
        query_vector (list): The query embedding vector
        top_k (int): Number of results to return
        
    Returns:
        list: List of similar points
        
    Raises:
        ValueError: If inputs are invalid
        RuntimeError: If search fails
    """
    if not query_vector or not isinstance(query_vector, list):
        raise ValueError("Query vector must be a non-empty list")
    
    if top_k <= 0:
        raise ValueError(f"top_k must be positive, got: {top_k}")
    
    try:
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k
        )

        if not results or not results.points:
            logger.warning("No similar chunks found in Qdrant")
            return []
        
        logger.info(f"Found {len(results.points)} similar chunks")
        return results.points
        
    except UnexpectedResponse as e:
        raise RuntimeError(f"Qdrant search failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to search similar chunks: {str(e)}")
