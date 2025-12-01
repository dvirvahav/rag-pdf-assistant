from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.rag_routes import router
from dotenv import load_dotenv
import sys
import os

load_dotenv()

# Add common module to path for auth imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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
