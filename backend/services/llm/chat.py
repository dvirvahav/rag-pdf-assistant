import os
import logging
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError, AuthenticationError

logger = logging.getLogger(__name__)


def refine_question(question: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Refine and clarify user questions for better document retrieval.
    NEVER raises exceptions - always returns a valid question string.

    Args:
        question: The original user question
        model: OpenAI model to use for refinement

    Returns:
        Refined question or original if refinement fails
    """
    # Always return original question for empty/invalid inputs
    if not question or not question.strip():
        return question

    # Safe refinement with comprehensive error handling
    try:
        # Lazy import of OpenAI client - only when actually needed
        from backend.services.llm.openai_client import get_openai_client
        client = get_openai_client()

        refinement_prompt = f"""You are a question clarification assistant. Rewrite user questions to be clear, specific, and well-formed for document search.

Rules:
- Correct grammar and spelling
- Expand abbreviations (e.g., "mgr" → "manager")
- Make ambiguous questions specific
- Keep the core intent unchanged
- Return only the clarified question, no explanation

Original: "{question}"
Clarified:"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": refinement_prompt}],
            temperature=0.1,  # Low temperature for consistency
            max_tokens=200   # Short responses
        )

        refined = response.choices[0].message.content.strip()

        # Validate refinement quality
        if refined and len(refined) > 10 and len(refined) < 500 and refined.lower() != question.lower():
            logger.info(f"Question refined: '{question}' → '{refined}'")
            return refined
        else:
            # Refinement not useful, use original
            logger.debug(f"Refinement not useful, using original: '{question}'")
            return question

    except Exception as e:
        # Any failure - log and return original question
        # This ensures backend stability
        logger.warning(f"Question refinement failed ({type(e).__name__}): {str(e)}, using original question")
        return question


def answer_question(
    question: str,
    context_chunks: list[str],
    model: str = "gpt-4o-mini",
    temperature: float = 0.1,
    max_tokens: Optional[int] = 1000
) -> str:
    """
    Uses GPT to answer a question using retrieved context from vector search.

    Args:
        question: The user's question
        context_chunks: Retrieved context chunks from vector search
        model: OpenAI model to use
        temperature: Response randomness (0-1, lower = more deterministic)
        max_tokens: Maximum response length

    Returns:
        The generated answer

    Raises:
        ValueError: If inputs are invalid
        ConnectionError: If cannot connect to OpenAI API
        RuntimeError: If API call fails
    """
    # Validate inputs
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if not isinstance(context_chunks, list):
        raise TypeError("context_chunks must be a list")

    if not context_chunks:
        raise ValueError("No context chunks provided. Upload and index a PDF first.")

    # Clean and validate chunks
    valid_chunks = []
    for i, chunk in enumerate(context_chunks):
        if not isinstance(chunk, str):
            logger.warning(f"Skipping non-string chunk at index {i}")
            continue
        cleaned = chunk.strip()
        if cleaned:
            valid_chunks.append(cleaned)

    if not valid_chunks:
        raise ValueError("All context chunks are empty")

    # Format context with chunk numbers for better reference
    context_block = "\n\n---\n\n".join(
        f"[Chunk {i+1}]\n{chunk}"
        for i, chunk in enumerate(valid_chunks)
    )

    # Token estimation warning
    estimated_tokens = len(context_block) // 4
    if estimated_tokens > 120000:  # gpt-4o-mini limit is 128k
        logger.warning(f"Context size large (~{estimated_tokens} tokens). May be truncated.")

    # System message for better instruction following
    system_message = """You are a precise document analysis assistant.
Answer questions based strictly on provided context. Be accurate, concise, and cite sources when possible."""

    prompt = f"""Use the following context to answer the question. The context includes document content and metadata.

**Analysis Rules:**
1. **Explicit Facts** (names, dates, numbers, specific details): Only use information directly stated in the context
2. **Document Type Inference**: You may identify document types from structural patterns:
   - Resume: "Experience", "Education", "Skills" sections, chronological work history
   - Invoice: Line items, amounts, totals, vendor/client information, payment terms
   - Report: Numbered sections, executive summary, table of contents, conclusions
   - Contract: Terms and conditions, legal clauses, signature blocks
   - Email: To/From/Subject headers, conversational tone
3. **Metadata**: Use provided document metadata (page count, author, creation date, file size)

**Response Guidelines:**
- Be concise and direct
- For factual answers: Quote relevant excerpts using quotation marks
- Cite chunk numbers when referencing specific sections (e.g., "According to Chunk 2...")
- If information is absent: State "This information is not available in the document"
- If question is ambiguous: Request clarification
- Do not make assumptions beyond what's in the context

**Context:**
{context_block}

**Question:** {question}

**Answer:**"""

    try:
        # Lazy import of OpenAI client - only when actually needed
        from backend.services.llm.openai_client import get_openai_client
        client = get_openai_client()

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        answer = response.choices[0].message.content

        if not answer or not answer.strip():
            raise RuntimeError("OpenAI returned an empty response")

        # Log token usage for monitoring
        usage = response.usage
        logger.info(f"Tokens used - Prompt: {usage.prompt_tokens}, "
                   f"Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")

        return answer.strip()

    except AuthenticationError as e:
        raise ValueError(f"OpenAI authentication failed. Check API key: {str(e)}")
    except RateLimitError as e:
        raise ValueError(f"Rate limit exceeded. Try again later: {str(e)}")
    except APIConnectionError as e:
        raise ConnectionError(f"Cannot connect to OpenAI API. Check internet: {str(e)}")
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise RuntimeError(f"Unexpected error during answer generation: {str(e)}")
