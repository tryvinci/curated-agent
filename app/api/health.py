from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.schemas import HealthCheckResponse
from app.services.redis_service import check_redis_connection
from app.celery_app import celery_app

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify system status
    """
    try:
        # Check Redis connection
        redis_connected = check_redis_connection()
        
        # Check Celery worker status
        celery_active = False
        try:
            # Check if any workers are active
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            celery_active = bool(stats and len(stats) > 0)
        except Exception:
            celery_active = False
        
        # Determine overall status
        status = "healthy" if redis_connected and celery_active else "degraded"
        if not redis_connected:
            status = "unhealthy"
        
        return HealthCheckResponse(
            status=status,
            redis_connected=redis_connected,
            celery_active=celery_active,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Curated Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }