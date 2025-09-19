# Curated Agent API Documentation

## Overview

The Curated Agent API is a comprehensive FastAPI application that provides creative workflow automation with AI agents, document processing, and multimedia generation capabilities.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API doesn't require authentication for most endpoints. However, external MCP servers may require their own authentication.

## Content Types

All API endpoints accept and return JSON unless otherwise specified.

```
Content-Type: application/json
```

## Error Handling

The API uses standard HTTP status codes and returns error responses in the following format:

```json
{
  "detail": "Error message description",
  "status_code": 400
}
```

## Health and Status

### Health Check

**GET** `/health`

Check the overall health of the system including Redis and Celery status.

**Response:**
```json
{
  "status": "healthy",
  "redis_connected": true,
  "celery_active": true,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### Root Endpoint

**GET** `/`

Get basic API information and available endpoints.

**Response:**
```json
{
  "message": "Curated Agent API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

## Creative Workflow API

### Submit Workflow Job

**POST** `/api/v1/workflow/submit`

Submit a creative workflow job for processing by AI agents.

**Request Body:**
```json
{
  "task_description": "Create a marketing campaign for a new product",
  "project_context": "Tech startup launching innovative app",
  "requirements": {
    "tone": "professional",
    "target_audience": "millennials"
  },
  "priority": 8
}
```

**Response:**
```json
{
  "job_id": "uuid4-string",
  "status": "pending",
  "message": "Creative workflow job submitted successfully"
}
```

### Get Job Status

**GET** `/api/v1/workflow/status/{job_id}`

Get the current status and results of a submitted job.

**Response:**
```json
{
  "job_id": "uuid4-string",
  "status": "completed",
  "result": {
    "success": true,
    "result": "Generated content...",
    "task_count": 3,
    "agent_count": 3
  },
  "error_message": null,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:05:00"
}
```

### List Jobs

**GET** `/api/v1/workflow/jobs`

List recent workflow jobs with optional filtering.

**Query Parameters:**
- `limit` (int): Maximum number of jobs to return (default: 10)
- `status` (string): Filter by job status (optional)

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "uuid4-string",
      "status": "completed",
      "task_description": "Create marketing campaign...",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:05:00"
    }
  ],
  "total": 1,
  "limit": 10
}
```

## Document Processing API

### Upload and Ingest Files

**POST** `/api/v1/documents/ingest/files`

Upload and ingest documents from files for knowledge base processing.

**Request:** Multipart form data with file uploads

**Response:**
```json
{
  "success": true,
  "message": "Successfully ingested 3 documents",
  "document_count": 3,
  "error": null
}
```

### Ingest Text Documents

**POST** `/api/v1/documents/ingest/text`

Ingest text documents directly into the knowledge base.

**Request Body:**
```json
{
  "texts": [
    "Document content text here...",
    "Another document content..."
  ],
  "metadata": [
    {"source": "manual", "title": "Document 1"},
    {"source": "manual", "title": "Document 2"}
  ]
}
```

### Search Documents

**POST** `/api/v1/documents/search`

Search through ingested documents using semantic search.

**Request Body:**
```json
{
  "query": "sustainable technology trends",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "query": "sustainable technology trends",
  "results": [
    {
      "text": "Document content snippet...",
      "score": 0.85,
      "metadata": {"source": "manual", "title": "Document 1"}
    }
  ],
  "error": null
}
```

### Query with AI Tools

**POST** `/api/v1/documents/query-with-tools`

Query documents using AI agent with access to MCP tools and media generation.

**Request Body:**
```json
{
  "query": "Create a marketing campaign image for sustainable technology",
  "system_message": "You are a creative assistant with access to document search and media generation tools"
}
```

**Response:**
```json
{
  "success": true,
  "query": "Create a marketing campaign image...",
  "response": "Based on the documents, I'll create an image...",
  "tools_used": [
    {"tool": "search_documents", "result": "Found relevant content"},
    {"tool": "generate_image", "result": "Image generated successfully"}
  ],
  "error": null
}
```

### Generate Media

**POST** `/api/v1/documents/generate-media`

Generate media (image, TTS, video) using external MCP servers.

**Request Body:**
```json
{
  "prompt": "A futuristic sustainable city with green technology",
  "media_type": "image",
  "style": "photorealistic",
  "size": "1024x1024"
}
```

**Response:**
```json
{
  "success": true,
  "media_type": "image",
  "prompt": "A futuristic sustainable city...",
  "result": {
    "url": "https://generated-image-url.com/image.jpg",
    "metadata": {"width": 1024, "height": 1024}
  },
  "error": null,
  "server_url": "http://localhost:8002"
}
```

### Document Statistics

**GET** `/api/v1/documents/stats`

Get statistics about the document index.

**Response:**
```json
{
  "success": true,
  "stats": {
    "available": true,
    "document_count": 25,
    "persist_dir": "./data/index_storage",
    "index_type": "VectorStoreIndex"
  }
}
```

### Clear Index

**DELETE** `/api/v1/documents/clear`

Clear all documents from the index.

**Response:**
```json
{
  "success": true,
  "message": "Index cleared successfully"
}
```

### External Servers

**GET** `/api/v1/documents/external-servers`

List available external MCP servers and their status.

**Response:**
```json
{
  "success": true,
  "servers": {
    "media_generation": {
      "url": "http://localhost:8001",
      "tools": ["generate_image", "generate_tts", "generate_video"],
      "status": "available"
    },
    "image_generation": {
      "url": "http://localhost:8002", 
      "status": "error",
      "error": "Connection refused"
    }
  }
}
```

### MCP Tools

**GET** `/api/v1/documents/mcp-tools`

List MCP tools available in LlamaIndex integration.

**Response:**
```json
{
  "success": true,
  "tools": [
    {
      "name": "generate_image",
      "description": "Generate images using external MCP server"
    },
    {
      "name": "generate_tts", 
      "description": "Generate text-to-speech using external MCP server"
    }
  ],
  "count": 2
}
```

## MCP Tools API

### List Available Tools

**GET** `/api/v1/mcp/tools`

List all available MCP tools with their descriptions.

**Response:**
```json
{
  "success": true,
  "tools": [
    {
      "name": "process_document",
      "description": "Process a document and extract information",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {"type": "string"},
          "extract_text": {"type": "boolean"}
        }
      }
    }
  ],
  "count": 1
}
```

### Get Tool Information

**GET** `/api/v1/mcp/tools/{tool_name}`

Get detailed information about a specific tool.

**Response:**
```json
{
  "success": true,
  "tool": {
    "name": "process_document",
    "description": "Process a document and extract information",
    "parameters": {
      "type": "object",
      "properties": {
        "path": {"type": "string"},
        "extract_text": {"type": "boolean"}
      }
    }
  }
}
```

### Execute Tool

**POST** `/api/v1/mcp/tools/execute`

Execute an MCP tool with given parameters.

**Request Body:**
```json
{
  "tool_name": "process_document",
  "parameters": {
    "path": "/path/to/document.pdf",
    "extract_text": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "tool_name": "process_document",
  "result": {
    "success": true,
    "path": "/path/to/document.pdf",
    "text_extracted": true,
    "message": "Document processed successfully"
  },
  "error": null
}
```

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

## Rate Limiting

Currently no rate limiting is implemented, but it may be added in future versions.

## Pagination

Some endpoints support pagination using query parameters:
- `limit`: Maximum number of items to return
- `offset`: Number of items to skip

## WebSocket Support

WebSocket support for real-time job status updates may be added in future versions.