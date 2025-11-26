from fastapi import FastAPI
from app.routers.rag_routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RAG Service",
    description="Retrieval-Augmented Generation: vector search + GPT answering",
    version="1.0.0",
)

app.include_router(router)
