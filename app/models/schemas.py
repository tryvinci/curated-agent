from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CreativeWorkflowRequest(BaseModel):
    """Request model for creative workflow jobs"""
    task_description: str = Field(..., description="Description of the creative task")
    project_context: Optional[str] = Field(None, description="Additional context for the project")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Specific requirements")
    priority: int = Field(default=5, ge=1, le=10, description="Job priority (1-10)")


class CreativeWorkflowResponse(BaseModel):
    """Response model for creative workflow results"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    result: Optional[Dict[str, Any]] = Field(None, description="Workflow result")
    error_message: Optional[str] = Field(None, description="Error message if job failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Job last update timestamp")


class JobSubmissionResponse(BaseModel):
    """Response model for job submission"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Initial job status")
    message: str = Field(..., description="Submission confirmation message")


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    redis_connected: bool = Field(..., description="Redis connection status")
    celery_active: bool = Field(..., description="Celery worker status")
    timestamp: datetime = Field(..., description="Health check timestamp")