import os
from dotenv import load_dotenv
from openai import OpenAI
from services.openai_client import get_openai_client

client = get_openai_client()


def answer_question(question: str, context_chunks: list[str]) -> str:
    """
    Uses GPT to answer a question using ONLY the retrieved context.
    """

    context_block = "\n\n".join(context_chunks)

    prompt = f"""
Use ONLY the following context to answer the question.
If the information is not present, answer: "The document does not contain this information."

Context:
{context_block}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
