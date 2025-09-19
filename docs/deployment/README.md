# Deployment Guide

## Overview

This guide covers different deployment strategies for the Curated Agent system, from local development to production deployment.

## Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM (16GB recommended for production)
- **Storage**: 50GB+ available space
- **Network**: Outbound HTTPS access for AI services

### Required Software
- **Docker**: 20.10+ and Docker Compose v2+
- **Python**: 3.12+ (for local development)
- **Git**: For source code management
- **Redis**: 7+ (if not using Docker)

## Quick Start (Local Development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/tryvinci/curated-agent.git
cd curated-agent

# Copy environment configuration
cp .env.example .env
```

### 2. Configure Environment

Edit the `.env` file with your settings:

```bash
# Required: Add your Anthropic API key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: External MCP servers
MCP_MEDIA_SERVER_URL=http://localhost:8001
MCP_IMAGE_SERVER_URL=http://localhost:8002
MCP_TTS_SERVER_URL=http://localhost:8003
MCP_VIDEO_SERVER_URL=http://localhost:8004

# Redis Configuration (uses Docker defaults)
REDIS_HOST=redis
REDIS_PORT=6379

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
```

### 3. Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or use the convenience script
./start.sh
```

### 4. Verify Deployment

```bash
# Check service health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Check service logs
docker-compose logs -f
```

## Development Deployment

### Local Python Development

For active development with hot reloading:

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Start Redis (if not using Docker)
redis-server

# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Start FastAPI with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Development with Docker

For development with consistent environment:

```bash
# Build and start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f app

# Access container for debugging
docker-compose exec app bash
```

### Running Tests

```bash
# Run tests locally
./run_tests.sh

# Or with Docker
docker-compose exec app pytest tests/ -v

# Run with coverage
docker-compose exec app pytest tests/ --cov=app --cov-report=html
```

## Production Deployment

### Environment Configuration

Create production environment file:

```bash
# Production .env
ANTHROPIC_API_KEY=your_production_api_key
DEBUG=false
LOG_LEVEL=WARNING

# Production Redis (external)
REDIS_HOST=redis.production.com
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_password

# Celery with authentication
CELERY_BROKER_URL=redis://:password@redis.production.com:6379/0
CELERY_RESULT_BACKEND=redis://:password@redis.production.com:6379/0

# External MCP servers
MCP_MEDIA_SERVER_URL=https://media.yourcompany.com
MCP_IMAGE_SERVER_URL=https://images.yourcompany.com
MCP_TTS_SERVER_URL=https://tts.yourcompany.com
MCP_VIDEO_SERVER_URL=https://video.yourcompany.com

# Storage configuration
LLAMA_INDEX_STORAGE_DIR=/app/data/production/index_storage
```

### Docker Production Setup

Create production Docker Compose file:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  worker:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
    command: celery -A app.celery_app worker --loglevel=warning --concurrency=2

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - app
    restart: unless-stopped

volumes:
  app_data:
  app_logs:
```

### Production Dockerfile

```dockerfile
# Dockerfile.prod
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY .env .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app/data /app/logs

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app_servers {
        server app:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/ssl/certs/your-cert.pem;
        ssl_certificate_key /etc/ssl/certs/your-key.pem;

        client_max_body_size 100M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;

        location / {
            proxy_pass http://app_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://app_servers/health;
            access_log off;
        }
    }
}
```

## Kubernetes Deployment

### Namespace and ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: curated-agent

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: curated-agent-config
  namespace: curated-agent
data:
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  LLAMA_INDEX_STORAGE_DIR: "/app/data/index_storage"
```

### Application Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: curated-agent-app
  namespace: curated-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: curated-agent-app
  template:
    metadata:
      labels:
        app: curated-agent-app
    spec:
      containers:
      - name: app
        image: curated-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: curated-agent-secrets
              key: anthropic-api-key
        envFrom:
        - configMapRef:
            name: curated-agent-config
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
          requests:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: curated-agent-data-pvc

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: curated-agent-service
  namespace: curated-agent
spec:
  selector:
    app: curated-agent-app
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Worker Deployment

```yaml
# k8s/worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: curated-agent-worker
  namespace: curated-agent
spec:
  replicas: 5
  selector:
    matchLabels:
      app: curated-agent-worker
  template:
    metadata:
      labels:
        app: curated-agent-worker
    spec:
      containers:
      - name: worker
        image: curated-agent:latest
        command: ["celery"]
        args: ["-A", "app.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: curated-agent-secrets
              key: anthropic-api-key
        envFrom:
        - configMapRef:
            name: curated-agent-config
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        resources:
          limits:
            memory: "4Gi"
            cpu: "2000m"
          requests:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: curated-agent-data-pvc
```

## Monitoring and Logging

### Health Monitoring

Set up monitoring for:
- Application health endpoints
- Redis connectivity
- Celery worker status
- External MCP server availability

### Log Configuration

```python
# app/core/logging.py
import logging
import sys
from app.core.config import get_settings

settings = get_settings()

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/app/logs/app.log')
        ]
    )
```

### Alerting Setup

Configure alerts for:
- High error rates
- Response time degradation
- Worker failures
- Redis connectivity issues
- External service failures

## Backup and Recovery

### Data Backup

```bash
# Backup document index
docker-compose exec app tar -czf /backup/index-$(date +%Y%m%d).tar.gz /app/data/index_storage

# Backup Redis data
docker-compose exec redis redis-cli BGSAVE
docker-compose exec redis cp /data/dump.rdb /backup/redis-$(date +%Y%m%d).rdb
```

### Recovery Process

```bash
# Restore document index
docker-compose exec app tar -xzf /backup/index-20240101.tar.gz -C /app/data/

# Restore Redis data
docker-compose stop redis
docker-compose exec redis cp /backup/redis-20240101.rdb /data/dump.rdb
docker-compose start redis
```

## Performance Tuning

### Application Tuning

```python
# app/core/config.py - Production settings
class Settings(BaseSettings):
    # Worker settings
    celery_worker_concurrency: int = 4
    celery_worker_prefetch_multiplier: int = 1
    
    # Redis settings
    redis_max_connections: int = 100
    redis_connection_pool_size: int = 50
    
    # API settings
    api_max_request_size: int = 100 * 1024 * 1024  # 100MB
    api_timeout: int = 300  # 5 minutes
```

### Database Optimization

```bash
# Redis optimization
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage
   docker-compose exec app ps aux --sort=-%mem | head
   
   # Monitor Redis memory
   docker-compose exec redis redis-cli INFO memory
   ```

2. **Slow Response Times**
   ```bash
   # Check API response times
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
   
   # Monitor worker queue
   docker-compose exec app celery -A app.celery_app inspect active
   ```

3. **Connection Issues**
   ```bash
   # Test Redis connection
   docker-compose exec app python -c "from app.services.redis_service import check_redis_connection; print(check_redis_connection())"
   
   # Test external MCP servers
   curl http://localhost:8001/health
   ```

### Log Analysis

```bash
# View application logs
docker-compose logs -f app

# Search for errors
docker-compose logs app | grep ERROR

# Monitor worker logs
docker-compose logs -f worker
```

This deployment guide provides comprehensive instructions for deploying the Curated Agent system in various environments, from local development to production Kubernetes clusters.