from fastapi import FastAPI
from app.routers.embedding_routes import router as embedding_router
from dotenv import load_dotenv

# Load env variables (OpenAI API key)
load_dotenv()

# Embedding / Ingestion service.
# Responsible for reading files, extracting text, cleaning,
# chunking, embedding, and storing vectors in Qdrant.
app = FastAPI(
    title="Embedding Service",
    description="Processes files into vector embeddings stored in Qdrant.",
    version="1.0.0"
)

app.include_router(embedding_router)
