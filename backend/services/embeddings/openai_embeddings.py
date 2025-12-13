import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError, AuthenticationError


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Creates embeddings for a list of text chunks.
    Returns a list of vectors (list of floats).
    Each chunk → one embedding vector.

    Args:
        chunks (list[str]): A list of textual chunks.

    Returns:
        list[list[float]]: A list of embedding vectors.
        
    Raises:
        TypeError: If chunks is not a list
        ValueError: If chunks is empty or contains invalid data
        OpenAIError: If OpenAI API call fails
    """
    if not isinstance(chunks, list):
        raise TypeError("Expected 'chunks' to be a list of strings")
    
    if not chunks:
        raise ValueError("Chunks list cannot be empty")
    
    # Validate all chunks are strings
    for i, chunk in enumerate(chunks):
        if not isinstance(chunk, str):
            raise TypeError(f"Chunk at index {i} is not a string: {type(chunk)}")
        if not chunk.strip():
            raise ValueError(f"Chunk at index {i} is empty or whitespace only")

    try:
        # Lazy import of OpenAI client - only when actually needed
        from backend.services.llm.openai_client import get_openai_client
        client = get_openai_client()

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunks
        )

        # response.data[i].embedding -> list[float]
        vectors = [item.embedding for item in response.data]

        return vectors
        
    except AuthenticationError as e:
        raise ValueError(f"OpenAI authentication failed. Check your API key: {str(e)}")
    except RateLimitError as e:
        raise ValueError(f"OpenAI rate limit exceeded. Please try again later: {str(e)}")
    except APIConnectionError as e:
        raise ConnectionError(f"Failed to connect to OpenAI API. Check your internet connection: {str(e)}")
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during embedding generation: {str(e)}")
