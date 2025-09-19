import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Curated Agent API - Barebones FastAPI + Redis + Celery"


def test_health_check():
    """Test health check endpoint"""
    with patch("app.api.health.check_redis_connection") as mock_redis:
        
        mock_redis.return_value = True
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "redis_connected" in data
        assert "celery_active" in data
        # Note: celery_active will be False since Celery is not available
        assert data["redis_connected"] == True
        assert data["celery_active"] == False


@patch("app.services.redis_service.get_redis_client")
@patch("app.tasks.api_caller.call_external_api.delay")
def test_submit_workflow_with_brand_and_requirements(mock_delay, mock_redis):
    """Test workflow submission endpoint with new brand/customer_requirements parameters"""
    mock_redis_client = MagicMock()
    mock_redis.return_value = mock_redis_client
    mock_delay.return_value = MagicMock()
    
    request_data = {
        "brand": "TechCorp",
        "customer_requirements": "Need a modern logo design for a tech startup"
    }
    
    response = client.post("/api/v1/workflow/submit", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert "message" in data
    
    # Verify that the Celery task was called with correct parameters
    mock_delay.assert_called_once()
    call_args = mock_delay.call_args
    assert "job_id" in call_args.kwargs
    assert call_args.kwargs["brand"] == "TechCorp"
    assert call_args.kwargs["customer_requirements"] == "Need a modern logo design for a tech startup"
    # Ensure api_url is not passed to the task
    assert "api_url" not in call_args.kwargs


def test_submit_workflow_missing_brand():
    """Test workflow submission endpoint with missing brand parameter"""
    request_data = {
        "customer_requirements": "Need a modern logo design for a tech startup"
    }
    
    response = client.post("/api/v1/workflow/submit", json=request_data)
    assert response.status_code == 422  # Validation error


def test_submit_workflow_missing_customer_requirements():
    """Test workflow submission endpoint with missing customer_requirements parameter"""
    request_data = {
        "brand": "TechCorp"
    }
    
    response = client.post("/api/v1/workflow/submit", json=request_data)
    assert response.status_code == 422  # Validation error


@patch("app.services.redis_service.get_redis_client")
def test_get_job_status_not_found(mock_redis):
    """Test getting status of non-existent job"""
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None
    mock_redis.return_value = mock_redis_client
    
    response = client.get("/api/v1/workflow/status/non-existent-job")
    assert response.status_code == 404


@patch("app.services.redis_service.get_redis_client")
def test_get_job_status_found(mock_redis):
    """Test getting status of existing job with new schema"""
    mock_redis_client = MagicMock()
    
    job_data = {
        "job_id": "test-job-123",
        "status": "completed",
        "brand": "TechCorp",
        "customer_requirements": "Need a modern logo design for a tech startup",
        "result": {"success": True, "output": "Test result"},
        "created_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-01T12:05:00"
    }
    
    mock_redis_client.get.return_value = json.dumps(job_data)
    mock_redis.return_value = mock_redis_client
    
    response = client.get("/api/v1/workflow/status/test-job-123")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "completed"
    assert data["brand"] == "TechCorp"
    assert data["customer_requirements"] == "Need a modern logo design for a tech startup"
    # Ensure api_url and method are not in the response
    assert "api_url" not in data
    assert "method" not in data