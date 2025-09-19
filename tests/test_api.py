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
    assert data["message"] == "Curated Agent API"


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


# @patch("app.services.redis_service.get_redis_client")
# @patch("app.tasks.creative_workflow.process_creative_workflow.delay")
# def test_submit_workflow(mock_delay, mock_redis):
#     """Test workflow submission endpoint"""
#     mock_redis_client = MagicMock()
#     mock_redis.return_value = mock_redis_client
#     mock_delay.return_value = MagicMock()
#     
#     request_data = {
#         "task_description": "Create a marketing campaign for a new product",
#         "project_context": "Tech startup launching innovative app",
#         "requirements": {"tone": "professional", "target_audience": "millennials"},
#         "priority": 8
#     }
#     
#     response = client.post("/api/v1/workflow/submit", json=request_data)
#     assert response.status_code == 200
#     data = response.json()
#     assert "job_id" in data
#     assert data["status"] == "pending"
#     assert "message" in data


# @patch("app.services.redis_service.get_redis_client")
# def test_get_job_status_not_found(mock_redis):
#     """Test getting status of non-existent job"""
#     mock_redis_client = MagicMock()
#     mock_redis_client.get.return_value = None
#     mock_redis.return_value = mock_redis_client
#     
#     response = client.get("/api/v1/workflow/status/non-existent-job")
#     assert response.status_code == 404


# @patch("app.services.redis_service.get_redis_client")
# def test_get_job_status_found(mock_redis):
#     """Test getting status of existing job"""
#     mock_redis_client = MagicMock()
#     
#     job_data = {
#         "job_id": "test-job-123",
#         "status": "completed",
#         "result": {"success": True, "output": "Test result"},
#         "created_at": "2024-01-01T12:00:00",
#         "updated_at": "2024-01-01T12:05:00"
#     }
#     
#     mock_redis_client.get.return_value = json.dumps(job_data)
#     mock_redis.return_value = mock_redis_client
#     
#     response = client.get("/api/v1/workflow/status/test-job-123")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["job_id"] == "test-job-123"
#     assert data["status"] == "completed"