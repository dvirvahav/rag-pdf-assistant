import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Read OpenAI key from .env
OPENAI_API_KEY = os.getenv("MY_OPENAI_KEY") or os.getenv("MY_OPENAI_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing MY_OPENAI_KEY in .env")

# Create ONE global client instance (shared across services)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_openai_client():
    """
    Returns a shared OpenAI client instance.
    Services should call this instead of creating their own clients.
    """
    return openai_client
