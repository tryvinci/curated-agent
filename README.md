# Curated Agent

A barebones FastAPI + Redis + Celery application for job processing. This application allows you to submit API call jobs that are processed asynchronously by Celery workers.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   FastAPI   │───▶│    Redis    │◀───│   Celery    │
│  (API Layer)│    │ (Job Queue) │    │  (Workers)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Redis**: In-memory data structure store used for job queuing and result storage
- **Celery**: Distributed task queue for background job processing
- **Job Management**: Submit, track, and manage API call jobs
- **Async Processing**: Non-blocking job execution with status tracking

## API Endpoints

- `POST /api/v1/workflow/submit` - Submit an API call job
- `GET /api/v1/workflow/status/{job_id}` - Get job status and results
- `GET /api/v1/workflow/jobs` - List recent jobs
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## Quick Start

### Prerequisites

- Python 3.8+
- Redis server
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd curated-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Redis configuration
```

4. Start Redis (if not running):
```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Or install locally
# On macOS: brew install redis && redis-server
# On Ubuntu: sudo apt-get install redis-server && redis-server
```

### Running the Application

#### Option 1: Manual Start

1. Start FastAPI server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Start Celery worker (in a separate terminal):
```bash
celery -A app.celery_app worker --loglevel=info
```

#### Option 2: Docker Compose

```bash
docker-compose up -d
```

### Usage Example

1. Submit an API call job:
```bash
curl -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "api_url": "https://httpbin.org/post",
    "method": "POST",
    "payload": {"message": "Hello World"},
    "timeout": 30
  }'
```

2. Check job status:
```bash
curl "http://localhost:8000/api/v1/workflow/status/{job_id}"
```

3. List recent jobs:
```bash
curl "http://localhost:8000/api/v1/workflow/jobs?limit=5"
```

## Request Schema

When submitting a job, use the following schema:

```json
{
  "api_url": "https://api.example.com/endpoint",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
  },
  "payload": {
    "key": "value"
  },
  "timeout": 30
}
```

## Response Schema

Job status response:

```json
{
  "job_id": "uuid",
  "status": "completed|processing|pending|failed",
  "api_url": "https://api.example.com/endpoint",
  "method": "POST",
  "result": {
    "success": true,
    "status_code": 200,
    "data": {...},
    "response_time_ms": 150
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:30Z"
}
```

## Configuration

Environment variables:

- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_DB`: Redis database (default: 0)
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL

## Development

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest tests/ -v
```

### Project Structure

```
app/
├── api/
│   ├── health.py       # Health check endpoints
│   └── workflow.py     # Job management endpoints
├── core/
│   └── config.py       # Application configuration
├── models/
│   └── schemas.py      # Pydantic models
├── services/
│   └── redis_service.py # Redis client
├── tasks/
│   └── api_caller.py   # Celery tasks
├── celery_app.py       # Celery configuration
└── main.py             # FastAPI application
```

## License

This project is licensed under the MIT License.