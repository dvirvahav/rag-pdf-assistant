"""
Embedding services for generating vector representations of text
"""
from .openai_embeddings import embed_chunks

__all__ = ["embed_chunks"]
