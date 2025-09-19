import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import httpx

from app.celery_app import celery_app
from app.services.redis_service import get_redis_client
from app.models.schemas import JobStatus

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def call_external_api(
    self,
    job_id: str,
    api_url: str,
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 30
):
    """
    Celery task that calls an external API and returns its output
    
    Args:
        job_id: Unique identifier for the job
        api_url: URL of the external API to call
        method: HTTP method (GET, POST, PUT, etc.)
        headers: Optional HTTP headers
        payload: Optional JSON payload for the request
        timeout: Request timeout in seconds
    """
    redis_client = get_redis_client()
    
    try:
        # Update job status to processing
        job_data = {
            "job_id": job_id,
            "status": JobStatus.PROCESSING.value,
            "api_url": api_url,
            "method": method,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        redis_client.setex(
            f"job:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(job_data)
        )
        
        logger.info(f"Starting API call for job {job_id}: {method} {api_url}")
        
        # Make the API call
        with httpx.Client(timeout=timeout) as client:
            if method.upper() == "GET":
                response = client.get(api_url, headers=headers or {})
            elif method.upper() == "POST":
                response = client.post(api_url, headers=headers or {}, json=payload)
            elif method.upper() == "PUT":
                response = client.put(api_url, headers=headers or {}, json=payload)
            elif method.upper() == "DELETE":
                response = client.delete(api_url, headers=headers or {})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Process the response
        result = {
            "success": response.is_success,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
        
        # Try to parse JSON response, fallback to text
        try:
            result["data"] = response.json()
        except Exception:
            result["data"] = response.text
        
        # Update job with results
        job_data.update({
            "status": JobStatus.COMPLETED.value if response.is_success else JobStatus.FAILED.value,
            "result": result,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        
        if response.is_success:
            logger.info(f"API call completed successfully for job {job_id}")
        else:
            logger.warning(f"API call completed with error status {response.status_code} for job {job_id}")
            job_data["error_message"] = f"API returned status code {response.status_code}"
        
        # Store final job status
        redis_client.setex(
            f"job:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(job_data)
        )
        
        return job_data
        
    except Exception as exc:
        error_msg = f"Task failed with exception: {str(exc)}"
        logger.error(f"Error in API call task {job_id}: {error_msg}")
        
        # Update job status to failed
        job_data = {
            "job_id": job_id,
            "status": JobStatus.FAILED.value,
            "error_message": error_msg,
            "updated_at": datetime.now(timezone.utc).isoformat()
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