from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.embedding_routes import router as embedding_router
from app.services.rabbitmq_consumer import embedding_consumer
from dotenv import load_dotenv

# Load env variables (OpenAI API key)
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Starts the RabbitMQ consumer on startup and stops it on shutdown.
    """
    # Startup: Start the RabbitMQ consumer
    print("Starting RabbitMQ consumer for file upload events...")
    embedding_consumer.start()
    
    yield
    
    # Shutdown: Stop the RabbitMQ consumer
    print("Stopping RabbitMQ consumer...")
    embedding_consumer.stop()


# Embedding / Ingestion service.
# Responsible for reading files, extracting text, cleaning,
# chunking, embedding, and storing vectors in Qdrant.
app = FastAPI(
    title="Embedding Service",
    description="Processes files into vector embeddings stored in Qdrant.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(embedding_router)
