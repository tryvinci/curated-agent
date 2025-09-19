import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import httpx

from app.celery_app import celery_app
from app.services.redis_service import get_redis_client
from app.models.schemas import JobStatus
from app.core.config import get_settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def call_external_api(
    self,
    job_id: str,
    brand: str,
    customer_requirements: str
):
    """
    Celery task that calls the downstream API with brand and customer requirements
    
    Args:
        job_id: Unique identifier for the job
        brand: Brand name for the API call
        customer_requirements: Customer requirements for the API call
    """
    redis_client = get_redis_client()
    settings = get_settings()
    
    try:
        # Get API URL from environment variable
        api_url = settings.downstream_api_url
        
        # Prepare the payload for the downstream API
        payload = {
            "brand": brand,
            "customer_requirements": customer_requirements
        }
        
        # Update job status to processing
        job_data = {
            "job_id": job_id,
            "status": JobStatus.PROCESSING.value,
            "brand": brand,
            "customer_requirements": customer_requirements,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        redis_client.setex(
            f"job:{job_id}",
            3600,  # 1 hour TTL
            json.dumps(job_data)
        )
        
        logger.info(f"Starting API call for job {job_id}: POST {api_url}")
        
        # Make the API call (always POST with the brand/requirements payload)
        headers = {"Content-Type": "application/json"}
        timeout = 30  # Default timeout
        
        with httpx.Client(timeout=timeout) as client:
            response = client.post(api_url, headers=headers, json=payload)
        
        logger.info(f"API response for job {job_id}: status_code={response.status_code} body='{response.text}'")

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