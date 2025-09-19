# Curated Agent

A Python FastAPI project with Redis, Celery, CrewAI, MCP tools, and LlamaIndex integration for creative workflow automation and document processing using Anthropic Claude.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Redis**: In-memory data store for job queuing and caching
- **Celery**: Distributed task queue for background processing
- **CrewAI**: Multi-agent framework for creative workflow automation
- **Anthropic Claude**: Advanced AI model for creative tasks
- **MCP Integration**: Model Context Protocol for tool and data source connections
- **LlamaIndex**: Document ingestion, processing, and intelligent search capabilities

## Architecture

The application follows a microservices architecture with enhanced AI capabilities:

1. **FastAPI Application**: Provides REST API endpoints for job submission, status checking, and new tool/document operations
2. **Redis**: Stores job data and serves as message broker for Celery
3. **Celery Workers**: Process creative workflow jobs in the background with enhanced tool access
4. **CrewAI Agents**: Specialized AI agents that collaborate on creative tasks with access to tools and knowledge
5. **MCP Tools**: Extensible tool system for AI agents to interact with external services
6. **LlamaIndex**: Document processing pipeline for knowledge base creation and semantic search

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

### MCP Tools
- `GET /api/v1/mcp/tools` - List available MCP tools
- `GET /api/v1/mcp/tools/{tool_name}` - Get information about a specific tool
- `POST /api/v1/mcp/tools/execute` - Execute an MCP tool with parameters

### Document Processing
- `POST /api/v1/documents/ingest/files` - Upload and ingest document files
- `POST /api/v1/documents/ingest/text` - Ingest text documents directly
- `POST /api/v1/documents/search` - Search through ingested documents
- `GET /api/v1/documents/stats` - Get document index statistics
- `DELETE /api/v1/documents/clear` - Clear all documents from index
- `GET /api/v1/documents/health` - Check document service health

## Usage Examples

### Submit a Creative Workflow Job with Document Context

```bash
# First, upload some documents for context
curl -X POST "http://localhost:8000/api/v1/documents/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Our company specializes in sustainable technology solutions for urban environments.",
      "Market research shows 73% of millennials prioritize eco-friendly products.",
      "Recent trends indicate growing demand for green technology in smart cities."
    ]
  }'

# Then submit a creative workflow job
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

### Use MCP Tools

```bash
# List available tools
curl "http://localhost:8000/api/v1/mcp/tools"

# Execute a tool
curl -X POST "http://localhost:8000/api/v1/mcp/tools/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "generate_content",
    "parameters": {
      "content_type": "blog_post",
      "prompt": "Write about sustainable technology trends",
      "context": "Environmental focus"
    }
  }'
```

### Search Documents

```bash
# Search through uploaded documents
curl -X POST "http://localhost:8000/api/v1/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sustainable technology trends",
    "top_k": 5
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
- `MCP_ENABLED`: Enable MCP tools integration (default: true)
- `LLAMA_INDEX_ENABLED`: Enable LlamaIndex document processing (default: true)
- `LLAMA_INDEX_STORAGE_DIR`: Directory for document index storage (default: ./data/index_storage)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)

## Enhanced Creative Workflow

The system now uses three specialized CrewAI agents with enhanced capabilities:

1. **Creative Director**: Develops creative strategy and oversees the process
   - Access to document knowledge base for research
   - Can execute MCP tools for additional context
   - Strategic planning and creative brief development

2. **Content Creator**: Generates the actual creative content
   - Search knowledge base for relevant information
   - Use MCP tools for content generation assistance
   - Creates engaging, contextually-aware content

3. **Quality Reviewer**: Reviews and refines the output for quality
   - Fact-checking using knowledge base search
   - Quality assessment and improvement suggestions
   - Ensures accuracy and consistency

### Enhanced Workflow Stages:
1. **Research & Strategy**: Agents search knowledge base and use available tools
2. **Content Creation**: Generate content with access to relevant context
3. **Quality Review**: Verify accuracy and refine output using available resources

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
├── main.py                     # FastAPI application with enhanced routers
├── celery_app.py              # Celery configuration
├── api/
│   ├── health.py              # Health check endpoints
│   ├── workflow.py            # Creative workflow endpoints
│   ├── mcp_tools.py           # MCP tools API endpoints
│   └── documents.py           # Document processing endpoints
├── core/
│   └── config.py              # Enhanced configuration
├── models/
│   └── schemas.py             # Pydantic models
├── services/
│   ├── redis_service.py       # Redis client
│   ├── creative_workflow.py   # Enhanced CrewAI service with tools
│   ├── mcp_integration.py     # MCP tools integration
│   └── llama_index_service.py # Document processing service
└── tasks/
    └── creative_workflow.py   # Enhanced Celery tasks
```

## Monitoring

- Health check endpoint: `/health`
- FastAPI automatic docs: `/docs`
- Celery flower (if installed): `http://localhost:5555`

## License

[Add your license here]