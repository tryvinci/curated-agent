# Curated Agent - FastAPI + Redis + Celery Job Processing

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Build the Repository

**CRITICAL**: Build and dependency installation may take 10-15 minutes. NEVER CANCEL these commands. Set timeout to 30+ minutes.

1. **Fix Requirements**: The requirements.txt has a dependency conflict. Update redis version:
   ```bash
   # Fix the redis version in requirements.txt to be compatible with celery
   sed -i 's/redis==5.0.1/redis==4.6.0/g' requirements.txt
   ```

2. **Environment Setup**:
   ```bash
   python -m pip install --upgrade pip
   cp .env.example .env
   # Edit .env if needed for custom Redis configuration
   ```

3. **Install Dependencies** -- takes 5-10 minutes, NEVER CANCEL:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # for testing
   # Set timeout to 30+ minutes due to potential network issues
   ```

4. **Basic Import Validation**:
   ```bash
   python -c "
   import app.main
   import app.celery_app  
   import app.services.redis_service
   import app.models.schemas
   print('All imports successful!')
   "
   ```

### Running the Application

**Option 1: Docker Compose (Recommended)**
```bash
# Build and start all services -- takes 5-10 minutes, NEVER CANCEL
docker compose up -d --build
# Set timeout to 30+ minutes for initial build

# Check service status
docker compose ps
docker compose logs -f app    # View FastAPI logs
docker compose logs -f worker # View Celery worker logs
```

**Option 2: Manual Start (Requires Redis)**
1. **Start Redis first** (required dependency):
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 --name redis redis:7-alpine
   
   # Or install locally:
   # Ubuntu: sudo apt-get install redis-server && redis-server
   # macOS: brew install redis && redis-server
   ```

2. **Start FastAPI server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start Celery worker** (in separate terminal):
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

### Testing

**Run Tests** -- takes 2-5 minutes, NEVER CANCEL:
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
python -m pytest tests/ -v
# Set timeout to 15+ minutes to be safe
```

**Test with Shell Scripts**:
```bash
./run_tests.sh      # Automated test runner
./test_setup.sh     # Basic setup validation
```

## Validation Scenarios

**ALWAYS** run these validation scenarios after making any changes:

### 1. Basic API Health Check
```bash
# Check if API is responding
curl http://localhost:8000/health
curl http://localhost:8000/

# Expected: JSON response with service status
```

### 2. Complete Job Submission Workflow
```bash
# 1. Submit a job
job_response=$(curl -s -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "api_url": "https://httpbin.org/post",
    "method": "POST", 
    "payload": {"test": "validation"},
    "timeout": 30
  }')

# Extract job_id from response
job_id=$(echo $job_response | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

# 2. Check job status (may need to wait a few seconds)
curl "http://localhost:8000/api/v1/workflow/status/$job_id"

# 3. List recent jobs
curl "http://localhost:8000/api/v1/workflow/jobs?limit=5"

# Expected: Job should progress from "pending" to "completed" status
```

### 3. Interactive API Documentation
- Visit: http://localhost:8000/docs
- Test endpoints interactively 
- **MANUAL VALIDATION REQUIRED**: Always test the complete workflow through the Swagger UI

## Common Issues and Fixes

### Dependency Conflicts
**Problem**: `celery[redis]==5.3.4 and redis==5.0.1` version conflict
**Solution**: Use `redis==4.6.0` instead of `redis==5.0.1`

### Network/PyPI Connection Issues
**Problem**: pip install fails with "certificate verify failed" or "Read timed out" errors
**Solution**: Use Docker Compose approach which bypasses local PyPI issues:
```bash
# Use Docker instead of local pip
docker compose up -d --build  # This works when pip fails
```
**Timing**: Network issues can cause pip installs to take 15+ minutes or fail entirely

### Redis Connection Issues  
**Problem**: Redis connection errors
**Solution**: 
```bash
# Check Redis is running
docker ps | grep redis
# Or for local Redis: redis-cli ping

# Restart Redis if needed
docker compose restart redis
```

### Docker Compose Version Warning
**Problem**: Warning about obsolete 'version' attribute
**Solution**: Safe to ignore - functionality works correctly 

### Import Errors in test_setup.sh
**Problem**: Script references non-existent modules 
**Solution**: Fixed in current version - only imports existing modules

## Project Structure

```
app/
├── api/
│   ├── health.py       # Health check endpoints
│   └── workflow.py     # Job management endpoints (main API)
├── core/
│   └── config.py       # Application configuration
├── models/
│   └── schemas.py      # Pydantic models and JobStatus enum
├── services/
│   └── redis_service.py # Redis client and connection checks
├── tasks/
│   └── api_caller.py   # Celery task for external API calls
├── celery_app.py       # Celery configuration
└── main.py             # FastAPI application entry point

Root files:
├── requirements.txt     # Python dependencies (fix redis version!)
├── requirements-test.txt # Test dependencies  
├── docker-compose.yml   # Service orchestration
├── Dockerfile          # Container build
├── start.sh            # Development startup script
├── run_tests.sh        # Test execution script
└── .env.example        # Environment configuration template
```

## Key Development Commands

**Always run these before committing changes**:
```bash
# No specific linting tools configured - validate manually:
python -m py_compile app/**/*.py  # Check syntax
python -c "import app.main"       # Test imports

# Run tests
python -m pytest tests/ -v

# Test Docker build  
docker compose build
```

## Environment Configuration

Key environment variables in `.env`:
- `DEBUG=false` - Debug mode
- `LOG_LEVEL=INFO` - Logging level
- `REDIS_HOST=localhost` - Redis host
- `REDIS_PORT=6379` - Redis port  
- `CELERY_BROKER_URL=redis://localhost:6379/0` - Celery broker
- `CELERY_RESULT_BACKEND=redis://localhost:6379/0` - Celery results

## Architecture Notes

- **FastAPI**: REST API layer with automatic OpenAPI docs
- **Redis**: Message queue and result storage 
- **Celery**: Distributed task queue for async job processing
- **HTTPX**: HTTP client for external API calls in tasks
- **Job Flow**: Submit → Queue → Process → Store Results → Retrieve

## Critical Timing Warnings

- **NEVER CANCEL**: Dependency installation (15-30 minutes if network issues occur)  
- **NEVER CANCEL**: Docker builds (5-10 minutes for initial build)
- **NEVER CANCEL**: Test execution (2-5 minutes)
- **Network Issues**: PyPI timeouts common - use Docker approach when pip fails
- Always set timeouts to 45+ minutes for build operations with network dependencies
- Always set timeouts to 15+ minutes for test operations
- Redis startup: ~1 second (very fast)
- Docker Compose services startup: ~1-2 minutes total

## Frequently Referenced Commands

```bash
# Quick status check (works even without full app running)
docker compose ps
docker exec curated-agent-redis-1 redis-cli ping  # Verify Redis

# Full status with health check (requires running app)
docker compose ps && curl -s http://localhost:8000/health | jq

# View logs
docker compose logs -f app worker redis

# Restart services  
docker compose restart

# Clean rebuild (measured timing: ~5-10 minutes)
docker compose down && docker compose up -d --build

# Basic validation without full dependencies
python -c "import app.main; import app.celery_app; print('Basic imports work')"

# Test Redis connectivity
docker exec curated-agent-redis-1 redis-cli SET test "working" && \
docker exec curated-agent-redis-1 redis-cli GET test
```