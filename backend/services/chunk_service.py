def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """
    Split text into overlapping chunks.
    This improves retrieval accuracy during the RAG step.

    Args:
        text (str): text.
        chunk_size (int): Number of characters per chunk.
        overlap (int): Number of overlapping characters between chunks.

    Returns:
        list: List of text chunks.
    """

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        # Move window forward with overlap
        start += chunk_size - overlap

    return chunks
