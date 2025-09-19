import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models.schemas import JobSubmissionResponse, JobStatus
from app.services.redis_service import get_redis_client
from app.tasks.api_caller import call_external_api

router = APIRouter(prefix="/api/v1/workflow", tags=["API Workflow"])


class APICallRequest(BaseModel):
    """Request model for API call jobs"""
    brand: str
    customer_requirements: str


class JobResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str
    brand: Optional[str] = None
    customer_requirements: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


@router.post("/submit", response_model=JobSubmissionResponse)
async def submit_api_call_job(
    request: APICallRequest,
    background_tasks: BackgroundTasks
) -> JobSubmissionResponse:
    """
    Submit an API call job for processing
    
    This endpoint:
    1. Validates the request
    2. Generates a unique job ID
    3. Stores initial job data in Redis
    4. Queues the job for processing with Celery
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Prepare job data (no longer includes api_url)
        job_data = {
            "job_id": job_id,
            "status": JobStatus.PENDING.value,
            "brand": request.brand,
            "customer_requirements": request.customer_requirements,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store job data in Redis
        redis_client = get_redis_client()
        redis_client.setex(
            f"job:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(job_data)
        )
        
        # Queue the job for processing (no longer passes api_url)
        call_external_api.delay(
            job_id=job_id,
            brand=request.brand,
            customer_requirements=request.customer_requirements
        )
        
        return JobSubmissionResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message=f"API call job {job_id} submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit job: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str) -> JobResponse:
    """
    Get the status and results of an API call job
    """
    try:
        redis_client = get_redis_client()
        job_data = redis_client.get(f"job:{job_id}")
        
        if not job_data:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        
        job_info = json.loads(job_data)
        
        return JobResponse(
            job_id=job_info["job_id"],
            status=job_info["status"],
            brand=job_info.get("brand"),
            customer_requirements=job_info.get("customer_requirements"),
            result=job_info.get("result"),
            error_message=job_info.get("error_message"),
            created_at=job_info["created_at"],
            updated_at=job_info["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/jobs")
async def list_jobs(limit: int = 10, status: Optional[str] = None) -> JSONResponse:
    """
    List recent jobs with optional status filtering
    """
    try:
        redis_client = get_redis_client()
        
        # Get all job keys
        job_keys = redis_client.keys("job:*")
        jobs = []
        
        for key in job_keys[:limit]:  # Limit results
            job_data = redis_client.get(key)
            if job_data:
                job_info = json.loads(job_data)
                
                # Filter by status if provided
                if status is None or job_info["status"] == status:
                    jobs.append({
                        "job_id": job_info["job_id"],
                        "status": job_info["status"],
                        "brand": job_info.get("brand", "N/A"),
                        "customer_requirements": job_info.get("customer_requirements", "N/A"),
                        "created_at": job_info["created_at"],
                        "updated_at": job_info["updated_at"]
                    })
        
        # Sort by creation time (most recent first)
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        return JSONResponse(content={
            "jobs": jobs,
            "total": len(jobs),
            "limit": limit
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list jobs: {str(e)}"
        )