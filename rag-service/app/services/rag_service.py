from app.services.openai_client import get_openai_client

client = get_openai_client()

def answer_question(question: str, context_chunks: list[str]) -> str:
    """
    Build a prompt out of user's question + retrieved context,
    and ask GPT for the final answer.
    """

    prompt = (
        "Answer the question strictly based on the following context:\n\n"
        + "\n---\n".join(context_chunks)
        + f"\n\nQuestion: {question}\nAnswer:"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]
