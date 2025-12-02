"""
Admin Service - Main Application Entry Point
Provides unified admin interface for managing the RAG PDF Assistant system.
"""
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

# Add parent directory to path to import common package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common.auth.dependencies import require_role

from app.routers.admin_routes import router as admin_router
from app.config import settings

# Application entrypoint for the Admin Service
app = FastAPI(
    title="Admin Service",
    description="Unified admin interface for RAG PDF Assistant system management",
    version=settings.VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register admin API routes
app.include_router(admin_router)

# Mount static files for admin UI
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(static_path)),
        name="static"
    )

    # Serve admin dashboard at root (with admin role protection)
    from fastapi import APIRouter
    ui_router = APIRouter(dependencies=[Depends(require_role("admin"))])

    @ui_router.get("/")
    async def admin_dashboard():
        """Serve admin dashboard"""
        return RedirectResponse(url="/static/index.html")

    app.include_router(ui_router)


@app.get("/health")
def health_check():
    """
    Root health check endpoint.
    """
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "healthy"
    }
