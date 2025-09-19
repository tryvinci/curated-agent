import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.celery_app import celery_app
from app.services.redis_service import get_redis_client
from app.services.creative_workflow import CreativeWorkflowService
from app.models.schemas import JobStatus

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_creative_workflow(
    self,
    job_id: str,
    task_description: str,
    project_context: Optional[str] = None,
    requirements: Optional[Dict[str, Any]] = None
):
    """
    Celery task to process creative workflow using CrewAI
    
    Args:
        job_id: Unique identifier for the job
        task_description: Description of the creative task
        project_context: Optional project context
        requirements: Optional requirements dictionary
    """
    redis_client = get_redis_client()
    
    try:
        # Update job status to processing
        job_data = {
            "job_id": job_id,
            "status": JobStatus.PROCESSING.value,
            "task_description": task_description,
            "project_context": project_context,
            "requirements": requirements,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        redis_client.setex(
            f"job:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(job_data)
        )
        
        logger.info(f"Starting creative workflow processing for job {job_id}")
        
        # Initialize and execute creative workflow
        workflow_service = CreativeWorkflowService()
        result = workflow_service.execute_workflow(
            task_description=task_description,
            project_context=project_context,
            requirements=requirements
        )
        
        # Update job with results
        if result.get("success"):
            job_data.update({
                "status": JobStatus.COMPLETED.value,
                "result": result,
                "updated_at": datetime.utcnow().isoformat()
            })
            logger.info(f"Creative workflow completed successfully for job {job_id}")
        else:
            job_data.update({
                "status": JobStatus.FAILED.value,
                "error_message": result.get("error", "Unknown error occurred"),
                "updated_at": datetime.utcnow().isoformat()
            })
            logger.error(f"Creative workflow failed for job {job_id}: {result.get('error')}")
        
        # Store final job status
        redis_client.setex(
            f"job:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(job_data)
        )
        
        return job_data
        
    except Exception as exc:
        error_msg = f"Task failed with exception: {str(exc)}"
        logger.error(f"Error in creative workflow task {job_id}: {error_msg}")
        
        # Update job status to failed
        job_data = {
            "job_id": job_id,
            "status": JobStatus.FAILED.value,
            "error_message": error_msg,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            redis_client.setex(
                f"job:{job_id}",
                3600,
                json.dumps(job_data)
            )
        except Exception as redis_error:
            logger.error(f"Failed to update job status in Redis: {redis_error}")
        
        # Re-raise the exception for Celery
        raise self.retry(exc=exc, countdown=60, max_retries=3)