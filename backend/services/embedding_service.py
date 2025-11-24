import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

# Read API key
OPENAI_API_KEY = os.getenv("MY_OPENAI_KEY")
print("API KEY:", OPENAI_API_KEY[:5])  # רק לבדיקה

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def embed_chunks(chunks: list) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )
    return [item.embedding for item in response.data]
