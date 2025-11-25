from openai import OpenAI

def answer_question(question: str, context_chunks: list) -> str:
    """
    Takes a user question and the retrieved context chunks (already selected),
    and generates a final answer using GPT.
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

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
