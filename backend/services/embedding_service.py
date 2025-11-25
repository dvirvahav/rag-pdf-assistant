import os
from dotenv import load_dotenv
from openai import OpenAI
from services.openai_client import get_openai_client

client = get_openai_client()


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Creates embeddings for a list of text chunks.
    Returns a list of vectors (list of floats).
    Each chunk → one embedding vector.

    Args:
        chunks (list[str]): A list of textual chunks.

    Returns:
        list[list[float]]: A list of embedding vectors.
    """
    if not isinstance(chunks, list):
        raise TypeError("Expected 'chunks' to be a list of strings")

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )

    # response.data[i].embedding -> list[float]
    vectors = [item.embedding for item in response.data]

    return vectors
