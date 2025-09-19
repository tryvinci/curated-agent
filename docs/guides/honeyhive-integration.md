# HoneyHive Integration Guide

## Overview

HoneyHive provides AI observability and monitoring for the Curated Agent system, allowing you to track LLM interactions, tool usage, workflow execution, and user feedback.

## What is HoneyHive?

HoneyHive is an AI observability platform that helps teams:
- Monitor AI model performance and costs
- Track tool usage and external service calls
- Analyze user interactions and feedback
- Debug issues in AI workflows
- Optimize AI application performance

## Setup

### 1. Get HoneyHive API Key

1. Sign up at [HoneyHive](https://honeyhive.ai)
2. Create a new project
3. Get your API key from the dashboard

### 2. Configure Environment

Add to your `.env` file:

```bash
# HoneyHive Configuration
HONEYHIVE_ENABLED=true
HONEYHIVE_API_KEY=your_honeyhive_api_key_here
HONEYHIVE_PROJECT_ID=your_project_id_here
```

### 3. Install Dependencies

HoneyHive is included in `requirements.txt`:

```bash
pip install honeyhive==0.1.23
```

## Features

### Automatic Monitoring

The system automatically tracks:

1. **Creative Workflow Execution**
   - Agent interactions
   - Task completion times
   - Success/failure rates
   - Full workflow context

2. **LLM Interactions**
   - Model calls to Anthropic Claude
   - Prompt and response logging
   - Token usage and costs
   - Response times

3. **Tool Usage**
   - MCP tool executions
   - Document processing operations
   - External API calls
   - Performance metrics

4. **External MCP Server Calls**
   - Image, TTS, video generation
   - Server response times
   - Error tracking
   - Success rates

### Manual Logging

You can also manually log events using the API:

#### Log LLM Interaction

```bash
curl -X POST "http://localhost:8000/api/v1/observability/sessions/session-123/events/llm" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet",
    "prompt": "Create a marketing campaign",
    "response": "Here is your campaign...",
    "duration_ms": 2500,
    "input_tokens": 50,
    "output_tokens": 200,
    "cost": 0.05
  }'
```

#### Log Tool Usage

```bash
curl -X POST "http://localhost:8000/api/v1/observability/sessions/session-123/events/tool" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "generate_image",
    "inputs": {"prompt": "sunset landscape"},
    "outputs": {"image_url": "https://..."},
    "success": true,
    "duration_ms": 3000
  }'
```

### User Feedback

Collect user feedback on AI-generated content:

```bash
curl -X POST "http://localhost:8000/api/v1/observability/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "rating": 4,
    "feedback_text": "Good content but could be more creative",
    "metadata": {
      "content_type": "social_media_post",
      "user_id": "user_456"
    }
  }'
```

## Monitoring Workflows

### Session Tracking

Each workflow execution gets a unique session ID that tracks all related activities:

```python
# Example workflow with session tracking
from app.services.honeyhive_service import get_honeyhive_service

honeyhive = get_honeyhive_service()
session_id = honeyhive.create_session_id("marketing-campaign")

# All subsequent operations will be tracked under this session
result = workflow_service.execute_workflow(
    task_description="Create social media campaign",
    session_id=session_id  # Passed automatically by decorated functions
)
```

### Viewing Session Metrics

```bash
curl "http://localhost:8000/api/v1/observability/sessions/session-123/metrics"
```

Response:
```json
{
  "success": true,
  "session_id": "session-123",
  "metrics": {
    "total_duration_ms": 15000,
    "llm_calls": 3,
    "tool_calls": 2,
    "total_cost": 0.12,
    "success_rate": 1.0
  }
}
```

## Observability API Endpoints

### Health Check

```bash
GET /api/v1/observability/health
```

Check if HoneyHive integration is working:

```json
{
  "success": true,
  "service": "HoneyHive",
  "status": "available",
  "enabled": true,
  "client_initialized": true
}
```

### Service Status

```bash
GET /api/v1/observability/status
```

Get detailed observability status:

```json
{
  "success": true,
  "status": {
    "honeyhive_available": true,
    "services": {
      "honeyhive": {
        "enabled": true,
        "client_initialized": true,
        "api_key_configured": true
      }
    }
  }
}
```

### Test Logging

```bash
POST /api/v1/observability/test-logging
```

Test the logging functionality:

```json
{
  "success": true,
  "test_session_id": "test-abc123-1640995200",
  "results": {
    "llm_logging": true,
    "tool_logging": true
  },
  "message": "Test logging completed"
}
```

## Dashboard Integration

### HoneyHive Dashboard

Once configured, you can view your data in the HoneyHive dashboard:

1. **Sessions**: View all workflow sessions with detailed traces
2. **Models**: Analyze LLM performance and costs
3. **Tools**: Monitor tool usage patterns and performance
4. **Feedback**: Analyze user feedback and ratings
5. **Analytics**: Get insights on usage patterns and optimization opportunities

### Key Metrics to Monitor

1. **Performance Metrics**
   - Average workflow completion time
   - LLM response times
   - Tool execution times
   - Error rates

2. **Cost Metrics**
   - Total LLM costs per workflow
   - Cost per token
   - Monthly spending trends

3. **Quality Metrics**
   - User satisfaction ratings
   - Success/failure rates
   - Retry frequencies

4. **Usage Metrics**
   - Daily active workflows
   - Popular tools and features
   - Peak usage times

## Best Practices

### 1. Session Management

Use descriptive session IDs:

```python
# Good: descriptive prefixes
session_id = honeyhive.create_session_id("marketing-campaign")
session_id = honeyhive.create_session_id("document-processing")

# Avoid: generic prefixes
session_id = honeyhive.create_session_id("operation")
```

### 2. Metadata Usage

Include relevant context in metadata:

```python
honeyhive.log_workflow_execution(
    session_id=session_id,
    workflow_name="creative_workflow",
    task_description=task_description,
    metadata={
        "user_id": "user_123",
        "company": "acme_corp",
        "campaign_type": "product_launch",
        "target_audience": "millennials",
        "budget": "mid_tier"
    }
)
```

### 3. Error Tracking

Always log errors with context:

```python
try:
    result = external_mcp_client.generate_image(prompt)
except Exception as e:
    honeyhive.log_external_mcp_call(
        session_id=session_id,
        server_name="image_generator",
        tool_name="generate_image",
        inputs={"prompt": prompt},
        outputs={},
        success=False,
        error_message=str(e),
        metadata={"retry_count": retry_count}
    )
```

### 4. Privacy Considerations

Be mindful of sensitive data in logs:

```python
# Don't log sensitive user data
honeyhive.log_llm_interaction(
    session_id=session_id,
    model="claude-3",
    prompt="Create content for user campaign",  # Anonymized
    response=response,
    metadata={
        "user_id": hash(actual_user_id),  # Hashed instead of raw
        "content_type": "marketing"
    }
)
```

## Troubleshooting

### Common Issues

1. **API Key Not Working**
   ```bash
   # Check configuration
   curl "http://localhost:8000/api/v1/observability/health"
   
   # Should return enabled: true
   ```

2. **Events Not Appearing**
   ```bash
   # Test logging functionality
   curl -X POST "http://localhost:8000/api/v1/observability/test-logging"
   
   # Check HoneyHive dashboard after 1-2 minutes
   ```

3. **High Latency**
   - HoneyHive logging is asynchronous and shouldn't impact performance
   - If issues persist, disable temporarily: `HONEYHIVE_ENABLED=false`

4. **Missing Dependencies**
   ```bash
   pip install honeyhive==0.1.23
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
# In .env file
LOG_LEVEL=DEBUG
HONEYHIVE_ENABLED=true

# Check application logs
docker-compose logs -f app | grep -i honeyhive
```

### Validation

Validate your integration:

```bash
# 1. Check health
curl "http://localhost:8000/api/v1/observability/health"

# 2. Test logging
curl -X POST "http://localhost:8000/api/v1/observability/test-logging"

# 3. Run a workflow and check HoneyHive dashboard
curl -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Test workflow for HoneyHive integration",
    "priority": 5
  }'
```

## Cost Optimization

### Token Tracking

Monitor token usage to optimize costs:

```python
# The system automatically tracks tokens for LLM calls
honeyhive.log_llm_interaction(
    session_id=session_id,
    model="claude-3-sonnet",
    prompt=prompt,
    response=response,
    input_tokens=count_tokens(prompt),
    output_tokens=count_tokens(response),
    cost=calculate_cost(input_tokens, output_tokens)
)
```

### Performance Monitoring

Track slow operations:

```python
start_time = time.time()
result = expensive_operation()
duration_ms = int((time.time() - start_time) * 1000)

if duration_ms > 5000:  # Flag slow operations
    honeyhive.log_tool_usage(
        session_id=session_id,
        tool_name="expensive_operation",
        metadata={"performance_flag": "slow", "threshold_ms": 5000}
    )
```

## Integration Examples

### Python Client

```python
import requests
from app.services.honeyhive_service import get_honeyhive_service

class MonitoredWorkflowClient:
    def __init__(self):
        self.honeyhive = get_honeyhive_service()
    
    def submit_workflow(self, task_description):
        session_id = self.honeyhive.create_session_id("api-client")
        
        # Submit workflow
        response = requests.post("http://localhost:8000/api/v1/workflow/submit", 
                               json={"task_description": task_description})
        
        # Log the API interaction
        self.honeyhive.log_tool_usage(
            session_id=session_id,
            tool_name="workflow_api",
            tool_inputs={"task_description": task_description},
            tool_outputs=response.json(),
            success=response.status_code == 200
        )
        
        return response.json()
```

### JavaScript Client

```javascript
class MonitoredWorkflowClient {
    constructor() {
        this.baseUrl = 'http://localhost:8000';
    }
    
    async submitWorkflow(taskDescription) {
        // Submit workflow
        const response = await fetch(`${this.baseUrl}/api/v1/workflow/submit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({task_description: taskDescription})
        });
        
        const result = await response.json();
        
        // Log interaction for monitoring
        await fetch(`${this.baseUrl}/api/v1/observability/sessions/${result.session_id}/events/tool`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                tool_name: 'workflow_api',
                inputs: {task_description: taskDescription},
                outputs: result,
                success: response.ok,
                duration_ms: Date.now() - startTime
            })
        });
        
        return result;
    }
}
```

This comprehensive HoneyHive integration provides full observability into your AI workflows, helping you monitor performance, track costs, and optimize your creative automation system.