import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError, AuthenticationError
from backend.services.llm.openai_client import get_openai_client

client = get_openai_client()


def answer_question(question: str, context_chunks: list[str]) -> str:
    """
    Uses GPT to answer a question using ONLY the retrieved context.
    
    Args:
        question (str): The user's question
        context_chunks (list[str]): Retrieved context chunks from vector search
        
    Returns:
        str: The generated answer
        
    Raises:
        ValueError: If inputs are invalid or OpenAI authentication fails
        ConnectionError: If cannot connect to OpenAI API
        RuntimeError: If OpenAI API call fails
    """
    # Validate inputs
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    if not isinstance(context_chunks, list):
        raise TypeError("context_chunks must be a list")
    
    if not context_chunks:
        raise ValueError("No context chunks provided. Please upload and index a PDF first.")
    
    # Validate context chunks
    for i, chunk in enumerate(context_chunks):
        if not isinstance(chunk, str):
            raise TypeError(f"Context chunk at index {i} is not a string")

    context_block = "\n\n".join(context_chunks)

    prompt = f"""
Use the following context to answer the question. The context includes document content and metadata about the document itself (such as page count, author, creation date, etc.).

For questions about the document type or general document characteristics, you may infer from content structure and common patterns (e.g., sections like "Experience", "Education", "Skills" indicate a resume; tables with amounts and line items suggest an invoice; numbered sections suggest a report or article).

For specific factual information, only use what's explicitly stated in the context.

If the information is not present in the context and cannot be reasonably inferred from document structure or patterns, answer: "The document does not contain this information."

Context:
{context_block}

Question:
{question}

Answer:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content
        
        if not answer:
            raise RuntimeError("OpenAI returned an empty response")
        
        return answer
        
    except AuthenticationError as e:
        raise ValueError(f"OpenAI authentication failed. Check your API key: {str(e)}")
    except RateLimitError as e:
        raise ValueError(f"OpenAI rate limit exceeded. Please try again later: {str(e)}")
    except APIConnectionError as e:
        raise ConnectionError(f"Failed to connect to OpenAI API. Check your internet connection: {str(e)}")
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during answer generation: {str(e)}")
