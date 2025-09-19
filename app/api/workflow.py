import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.schemas import (
    CreativeWorkflowRequest,
    CreativeWorkflowResponse,
    JobSubmissionResponse,
    JobStatus
)
from app.services.redis_service import get_redis_client
from app.tasks.creative_workflow import process_creative_workflow

router = APIRouter(prefix="/api/v1/workflow", tags=["Creative Workflow"])


@router.post("/submit", response_model=JobSubmissionResponse)
async def submit_creative_workflow(
    request: CreativeWorkflowRequest,
    background_tasks: BackgroundTasks
) -> JobSubmissionResponse:
    """
    Submit a creative workflow job for processing
    
    This endpoint:
    1. Validates the request
    2. Generates a unique job ID
    3. Stores initial job data in Redis
    4. Queues the job for processing with Celery
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Prepare job data
        job_data = {
            "job_id": job_id,
            "status": JobStatus.PENDING.value,
            "task_description": request.task_description,
            "project_context": request.project_context,
            "requirements": request.requirements,
            "priority": request.priority,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Store job data in Redis
        redis_client = get_redis_client()
        redis_client.setex(
            f"job:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(job_data)
        )
        
        # Queue the job for processing
        process_creative_workflow.delay(
            job_id=job_id,
            task_description=request.task_description,
            project_context=request.project_context,
            requirements=request.requirements
        )
        
        return JobSubmissionResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message=f"Creative workflow job {job_id} submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit job: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=CreativeWorkflowResponse)
async def get_job_status(job_id: str) -> CreativeWorkflowResponse:
    """
    Get the status and results of a creative workflow job
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
        
        return CreativeWorkflowResponse(
            job_id=job_info["job_id"],
            status=JobStatus(job_info["status"]),
            result=job_info.get("result"),
            error_message=job_info.get("error_message"),
            created_at=datetime.fromisoformat(job_info["created_at"]),
            updated_at=datetime.fromisoformat(job_info["updated_at"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/jobs")
async def list_jobs(limit: int = 10, status: Optional[JobStatus] = None) -> JSONResponse:
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
                if status is None or job_info["status"] == status.value:
                    jobs.append({
                        "job_id": job_info["job_id"],
                        "status": job_info["status"],
                        "task_description": job_info["task_description"][:100] + "..." if len(job_info["task_description"]) > 100 else job_info["task_description"],
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