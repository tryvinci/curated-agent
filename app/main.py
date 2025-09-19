import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.health import router as health_router
from app.api.workflow import router as workflow_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up Curated Agent API...")
    yield
    # Shutdown
    logger.info("Shutting down Curated Agent API...")


# Create FastAPI application
app = FastAPI(
    title="Curated Agent API",
    description="A barebones FastAPI application with Redis and Celery for job processing. Celery workers call external APIs and return their output.",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(workflow_router)


# Root endpoint
@app.get("/")
async def root():
    """Get basic API information and available endpoints"""
    return {
        "message": "Curated Agent API - Barebones FastAPI + Redis + Celery",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "available_endpoints": [
            "POST /api/v1/workflow/submit - Submit job for processing",
            "GET /api/v1/workflow/status/{job_id} - Get job status",
            "GET /api/v1/workflow/jobs - List recent jobs"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )