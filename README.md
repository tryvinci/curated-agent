# Curated Agent

A Python FastAPI project with Redis, Celery, and CrewAI integration for creative workflow automation using Anthropic Claude.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Redis**: In-memory data store for job queuing and caching
- **Celery**: Distributed task queue for background processing
- **CrewAI**: Multi-agent framework for creative workflow automation
- **Anthropic Claude**: Advanced AI model for creative tasks

## Architecture

The application follows a microservices architecture:

1. **FastAPI Application**: Provides REST API endpoints for job submission and status checking
2. **Redis**: Stores job data and serves as message broker for Celery
3. **Celery Workers**: Process creative workflow jobs in the background
4. **CrewAI Agents**: Specialized AI agents that collaborate on creative tasks

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd curated-agent
```

2. Copy the environment file and configure:
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

3. Start the services:
```bash
docker-compose up -d
```

4. The API will be available at `http://localhost:8000`

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Redis:
```bash
redis-server
```

3. Start Celery worker:
```bash
celery -A app.celery_app worker --loglevel=info
```

4. Start FastAPI application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Health Check
- `GET /health` - Check system health status

### Creative Workflow
- `POST /api/v1/workflow/submit` - Submit a creative workflow job
- `GET /api/v1/workflow/status/{job_id}` - Get job status and results
- `GET /api/v1/workflow/jobs` - List recent jobs

## Usage Examples

### Submit a Creative Workflow Job

```bash
curl -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a marketing campaign for a new eco-friendly product",
    "project_context": "Sustainable technology startup",
    "requirements": {
      "tone": "professional yet approachable",
      "target_audience": "environmentally conscious consumers",
      "channels": ["social_media", "blog_posts", "email"]
    },
    "priority": 8
  }'
```

### Check Job Status

```bash
curl "http://localhost:8000/api/v1/workflow/status/{job_id}"
```

## Environment Variables

- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL
- `ANTHROPIC_API_KEY`: Your Anthropic API key (**required**)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)

## Creative Workflow

The system uses three specialized CrewAI agents:

1. **Creative Director**: Develops creative strategy and oversees the process
2. **Content Creator**: Generates the actual creative content
3. **Quality Reviewer**: Reviews and refines the output for quality

Each job goes through multiple stages:
1. Strategy development
2. Content creation
3. Quality review and refinement

## Development

### Running Tests

```bash
pip install -r requirements-test.txt
pytest
```

### Code Structure

```
app/
├── __init__.py
├── main.py              # FastAPI application
├── celery_app.py        # Celery configuration
├── api/
│   ├── health.py        # Health check endpoints
│   └── workflow.py      # Creative workflow endpoints
├── core/
│   └── config.py        # Application configuration
├── models/
│   └── schemas.py       # Pydantic models
├── services/
│   ├── redis_service.py     # Redis client
│   └── creative_workflow.py # CrewAI service
└── tasks/
    └── creative_workflow.py # Celery tasks
```

## Monitoring

- Health check endpoint: `/health`
- FastAPI automatic docs: `/docs`
- Celery flower (if installed): `http://localhost:5555`

## License

[Add your license here]