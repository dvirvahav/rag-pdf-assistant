from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.rag_routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RAG Service",
    description="Retrieval-Augmented Generation: vector search + GPT answering",
    version="1.0.0",
)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
