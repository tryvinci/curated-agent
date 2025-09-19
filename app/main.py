import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.health import router as health_router

# Try to import workflow router, but handle missing dependencies gracefully
try:
    from app.api.workflow import router as workflow_router
    WORKFLOW_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Workflow router not available due to missing dependencies: {e}")
    workflow_router = None
    WORKFLOW_AVAILABLE = False

# Import new MCP and document processing routers
try:
    from app.api.mcp_tools import router as mcp_router
    MCP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"MCP tools router not available due to missing dependencies: {e}")
    mcp_router = None
    MCP_AVAILABLE = False

try:
    from app.api.documents import router as documents_router
    DOCUMENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Documents router not available due to missing dependencies: {e}")
    documents_router = None
    DOCUMENTS_AVAILABLE = False

try:
    from app.api.observability import router as observability_router
    OBSERVABILITY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Observability router not available due to missing dependencies: {e}")
    observability_router = None
    OBSERVABILITY_AVAILABLE = False

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
    description="A FastAPI application with Redis, Celery, CrewAI, MCP tools, LlamaIndex, and HoneyHive for creative workflow automation, document processing, and AI observability",
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
if WORKFLOW_AVAILABLE:
    app.include_router(workflow_router)
if MCP_AVAILABLE:
    app.include_router(mcp_router)
if DOCUMENTS_AVAILABLE:
    app.include_router(documents_router)
if OBSERVABILITY_AVAILABLE:
    app.include_router(observability_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )