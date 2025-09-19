# Architecture Overview

## System Architecture

The Curated Agent system follows a microservices architecture designed for scalability, reliability, and extensibility. The system is composed of several interconnected components that work together to provide AI-powered creative workflow automation.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │───▶│   FastAPI App   │───▶│      Redis      │
│  (Web, Mobile)  │    │   (API Layer)   │    │  (Job Queue)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                                │              ┌─────────────────┐
                                │              │  Celery Workers │
                                │              │  (Background)   │
                                │              └─────────────────┘
                                │                        │
                                │                        ▼
                                │              ┌─────────────────┐
                                │              │    CrewAI       │
                                │              │   Workflow      │
                                │              └─────────────────┘
                                │                        │
                                ▼              ┌────────┼────────┐
                      ┌─────────────────┐      │        │        │
                      │   Document      │      ▼        ▼        ▼
                      │   Processing    │ ┌─────────┐ ┌──────┐ ┌──────┐
                      │  (LlamaIndex)   │ │MCP Tools│ │Claude│ │Media │
                      └─────────────────┘ │(Local)  │ │ LLM  │ │ Gen  │
                                │         └─────────┘ └──────┘ └──────┘
                                ▼                              │
                      ┌─────────────────┐                     ▼
                      │   External MCP  │           ┌─────────────────┐
                      │    Servers      │           │  External MCP   │
                      │ (Image/TTS/Vid) │           │    Servers      │
                      └─────────────────┘           │ (Distributed)   │
                                                    └─────────────────┘
```

## Core Components

### 1. FastAPI Application Layer

**Purpose**: HTTP API gateway and request routing
**Location**: `app/main.py`, `app/api/`

The FastAPI application serves as the main entry point for all client requests. It provides:
- RESTful API endpoints
- Request validation using Pydantic models
- Automatic OpenAPI/Swagger documentation
- Health monitoring endpoints
- Error handling and logging

**Key Features:**
- Asynchronous request handling
- Middleware for CORS and logging
- Graceful dependency handling
- Route-based modular design

### 2. Redis (Message Broker & Cache)

**Purpose**: Job queuing, caching, and data persistence
**Technology**: Redis 7+ with persistence enabled

Redis serves multiple roles in the architecture:
- **Job Queue**: Stores workflow job data and status
- **Celery Broker**: Message broker for background tasks
- **Cache**: Temporary storage for frequently accessed data
- **Session Storage**: Could be extended for user sessions

**Configuration:**
- Persistent storage with AOF (Append Only File)
- Memory optimization for job data
- TTL (Time To Live) for temporary data

### 3. Celery Workers

**Purpose**: Background task processing
**Location**: `app/tasks/`, `app/celery_app.py`

Celery workers handle asynchronous processing of creative workflows:
- **Horizontal Scaling**: Multiple workers can process jobs in parallel
- **Retry Logic**: Failed jobs are retried with exponential backoff
- **Task Monitoring**: Job progress and status tracking
- **Priority Queue**: Higher priority jobs are processed first

**Worker Types:**
- **Workflow Workers**: Process CrewAI creative workflows
- **Document Workers**: Handle document ingestion and processing
- **Media Workers**: Process media generation requests

### 4. CrewAI Workflow Engine

**Purpose**: Multi-agent AI orchestration
**Location**: `app/services/creative_workflow.py`

The CrewAI system orchestrates multiple AI agents working together:

#### Agent Architecture:
```
Creative Director (Strategy)
        │
        ▼
Content Creator (Generation) ◄─── Knowledge Base
        │                           │
        ▼                           ▼
Quality Reviewer (Refinement) ◄─ MCP Tools
```

**Agents:**
1. **Creative Director**: Strategic planning and oversight
2. **Content Creator**: Content generation and creativity  
3. **Quality Reviewer**: Quality assurance and refinement

**Agent Capabilities:**
- Access to document knowledge base
- MCP tool execution
- Media generation capabilities
- Inter-agent communication
- Task delegation and coordination

### 5. Document Processing (LlamaIndex)

**Purpose**: Intelligent document handling and search
**Location**: `app/services/llama_index_service.py`

LlamaIndex provides advanced document processing capabilities:
- **Vector Storage**: Semantic document embeddings
- **Intelligent Retrieval**: Context-aware document search
- **Multi-format Support**: PDF, DOCX, text files
- **Agent Integration**: Tools for AI agents to search knowledge

**Features:**
- Persistent vector storage
- Incremental document updates
- Semantic similarity search
- Metadata filtering
- Tool integration for AI agents

### 6. MCP (Model Context Protocol) Integration

**Purpose**: Extensible tool system
**Location**: `app/services/mcp_integration.py`, `app/services/external_mcp_client.py`

MCP provides a standardized way to integrate tools and external services:

#### Local MCP Tools:
- Document processing
- Data search
- Content generation utilities

#### External MCP Servers:
- Image generation services
- Text-to-speech services
- Video generation services
- Custom tool integrations

### 7. External MCP Servers

**Purpose**: Specialized media generation services
**Technology**: Distributed microservices

External MCP servers provide specialized capabilities:
- **Image Generation**: AI-powered image creation
- **TTS Generation**: Text-to-speech conversion
- **Video Generation**: AI video creation
- **Custom Services**: Extensible for additional capabilities

## Data Flow

### 1. Creative Workflow Process

```
Client Request → FastAPI → Redis (Job Storage) → Celery Worker → CrewAI Agents
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   Agent Tools   │
                                            │                 │
                                            │ • Search Docs   │
                                            │ • Generate Media│
                                            │ • Execute MCP   │
                                            │ • Quality Check │
                                            └─────────────────┘
                                                      │
                                                      ▼
Result Storage ◄─ Redis ◄─── Status Updates ◄─ Agent Results
```

### 2. Document Processing Flow

```
File Upload → FastAPI → Temporary Storage → LlamaIndex Processing
                                                   │
                                                   ▼
                                          Vector Embeddings
                                                   │
                                                   ▼
                                          Persistent Storage
                                                   │
                                                   ▼
                                          Available for Search
```

### 3. Media Generation Flow

```
Media Request → FastAPI → External MCP Client → External MCP Server
                    │                                   │
                    ▼                                   ▼
            Agent Tool Access ◄──────── Media Result ◄─┘
```

## Scalability Considerations

### Horizontal Scaling

1. **Multiple FastAPI Instances**: Load balanced behind reverse proxy
2. **Celery Worker Scaling**: Auto-scaling based on queue length
3. **Redis Clustering**: Distributed Redis for high availability
4. **External MCP Services**: Independent scaling of media services

### Performance Optimization

1. **Async/Await**: Non-blocking request handling
2. **Connection Pooling**: Efficient database/Redis connections
3. **Caching Strategy**: Multi-level caching for frequently accessed data
4. **Background Processing**: Offload heavy tasks to workers

### Reliability Features

1. **Health Checks**: Comprehensive system monitoring
2. **Circuit Breakers**: Prevent cascade failures
3. **Retry Logic**: Exponential backoff for transient failures
4. **Graceful Degradation**: System works with partial failures

## Security Architecture

### API Security

1. **Input Validation**: Pydantic model validation
2. **Error Handling**: Secure error messages
3. **CORS Configuration**: Controlled cross-origin access
4. **Rate Limiting**: (Future implementation)

### Data Security

1. **Environment Variables**: Sensitive configuration
2. **API Key Management**: Secure external service authentication
3. **Data Isolation**: Tenant separation (future)
4. **Audit Logging**: Request/response tracking

## Deployment Architecture

### Container Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                       Docker Host                          │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │   FastAPI    │ │    Redis     │ │   Celery     │      │
│  │  Container   │ │  Container   │ │  Container   │      │
│  └──────────────┘ └──────────────┘ └──────────────┘      │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐                       │
│  │  External    │ │  Document    │                       │
│  │  MCP Servers │ │   Storage    │                       │
│  └──────────────┘ └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Volume Strategy

- **Document Storage**: Persistent volume for LlamaIndex data
- **Redis Data**: Persistent volume for job and cache data
- **Log Storage**: Centralized logging volume
- **Configuration**: Config maps for environment-specific settings

## Monitoring and Observability

### Health Monitoring

1. **Application Health**: `/health` endpoint
2. **Component Health**: Individual service checks
3. **Performance Metrics**: Response times and throughput
4. **Error Rates**: Exception tracking and alerting

### Logging Strategy

1. **Structured Logging**: JSON format for parsing
2. **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
3. **Contextual Information**: Request IDs and user context
4. **Centralized Collection**: Log aggregation system

### Future Observability

1. **Metrics Collection**: Prometheus/Grafana integration
2. **Distributed Tracing**: Request flow across services
3. **Alerting**: Automated incident response
4. **Dashboard**: Real-time system monitoring

## Technology Stack

### Core Technologies
- **Python 3.12+**: Primary programming language
- **FastAPI**: Web framework for APIs
- **Redis**: Message broker and cache
- **Celery**: Distributed task queue
- **Docker**: Containerization platform

### AI/ML Technologies
- **CrewAI**: Multi-agent AI framework
- **Anthropic Claude**: Language model
- **LlamaIndex**: Document processing and search
- **MCP Protocol**: Tool integration standard

### Infrastructure Technologies
- **Docker Compose**: Local orchestration
- **Kubernetes**: Production orchestration (future)
- **Nginx**: Reverse proxy and load balancer (production)
- **PostgreSQL**: Relational database (future extension)

This architecture is designed to be robust, scalable, and maintainable while providing the flexibility needed for AI-powered creative workflows.