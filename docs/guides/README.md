# User Guide

## Getting Started

This guide will help you use the Curated Agent system to create AI-powered creative workflows, process documents, and generate multimedia content.

## Prerequisites

- Curated Agent system deployed and running
- Access to the API at `http://localhost:8000` (or your deployment URL)
- Anthropic API key configured
- Optional: External MCP servers for media generation

## Quick Start

### 1. Verify System Health

First, check that all components are running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "redis_connected": true,
  "celery_active": true,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 2. View API Documentation

Open your browser to see the interactive API documentation:
```
http://localhost:8000/docs
```

### 3. Submit Your First Creative Workflow

```bash
curl -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a social media post about sustainable technology",
    "project_context": "Environmental tech company launching new product",
    "requirements": {
      "tone": "professional yet engaging",
      "target_audience": "tech-savvy environmentalists",
      "platform": "LinkedIn"
    },
    "priority": 5
  }'
```

Response:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "Creative workflow job a1b2c3d4-e5f6-7890-abcd-ef1234567890 submitted successfully"
}
```

### 4. Check Job Status

```bash
curl "http://localhost:8000/api/v1/workflow/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

## Core Features

### Creative Workflow Automation

The system uses three AI agents working together:

1. **Creative Director**: Develops strategy and creative brief
2. **Content Creator**: Generates actual content
3. **Quality Reviewer**: Reviews and refines the output

#### Workflow Process:

```
Your Request → Creative Director (Strategy) → Content Creator (Generation) → Quality Reviewer (Refinement) → Final Result
```

#### Example Workflow Request:

```json
{
  "task_description": "Create a comprehensive marketing campaign for a new eco-friendly smartphone",
  "project_context": "Startup company targeting environmentally conscious millennials and Gen Z consumers",
  "requirements": {
    "tone": "innovative and inspiring",
    "target_audience": "environmentally conscious tech users aged 18-35",
    "deliverables": ["social media content", "blog post", "email campaign"],
    "brand_values": ["sustainability", "innovation", "transparency"],
    "budget": "mid-tier startup budget",
    "timeline": "2 weeks"
  },
  "priority": 8
}
```

### Document Processing and Knowledge Base

#### Upload Documents

Upload files to create a searchable knowledge base:

```bash
curl -X POST "http://localhost:8000/api/v1/documents/ingest/files" \
  -F "files=@company_info.pdf" \
  -F "files=@product_specs.docx" \
  -F "files=@market_research.txt"
```

#### Add Text Documents

Add text content directly:

```bash
curl -X POST "http://localhost:8000/api/v1/documents/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Our company was founded in 2020 with a mission to create sustainable technology solutions...",
      "Market research shows that 78% of consumers consider environmental impact when making tech purchases..."
    ],
    "metadata": [
      {"source": "company_about", "title": "Company Background", "date": "2024-01-01"},
      {"source": "market_research", "title": "Consumer Preferences Study", "date": "2023-12-15"}
    ]
  }'
```

#### Search Documents

Search through your knowledge base:

```bash
curl -X POST "http://localhost:8000/api/v1/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are current consumer preferences for sustainable technology?",
    "top_k": 3
  }'
```

### AI-Powered Query with Tools

Use AI agents that can search documents AND generate media:

```bash
curl -X POST "http://localhost:8000/api/v1/documents/query-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a marketing image concept for our sustainable smartphone based on our research data",
    "system_message": "You are a creative marketing assistant with access to company documents and media generation tools. Use the knowledge base to inform your creative decisions."
  }'
```

This will:
1. Search the knowledge base for relevant information
2. Use that information to create an image concept
3. Potentially generate the actual image using external MCP services

### Media Generation

#### Generate Images

```bash
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A sleek, modern smartphone with green technology elements, surrounded by nature, photorealistic style",
    "media_type": "image",
    "style": "photorealistic",
    "size": "1024x1024"
  }'
```

#### Generate Text-to-Speech

```bash
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Introducing the future of sustainable technology - our new eco-friendly smartphone that doesn't compromise on performance",
    "media_type": "tts",
    "voice": "professional",
    "format": "mp3"
  }'
```

#### Generate Videos

```bash
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show the lifecycle of a sustainable smartphone from recycled materials to final product",
    "media_type": "video",
    "duration": 30,
    "style": "corporate"
  }'
```

## Advanced Usage

### MCP Tools Integration

#### List Available Tools

```bash
curl "http://localhost:8000/api/v1/mcp/tools"
```

#### Execute Specific Tools

```bash
curl -X POST "http://localhost:8000/api/v1/mcp/tools/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "process_document",
    "parameters": {
      "path": "/path/to/document.pdf",
      "extract_text": true
    }
  }'
```

#### Check External MCP Servers

```bash
curl "http://localhost:8000/api/v1/documents/external-servers"
```

### Workflow Management

#### List All Jobs

```bash
curl "http://localhost:8000/api/v1/workflow/jobs?limit=20&status=completed"
```

#### Monitor Job Progress

```bash
# Check status periodically
while true; do
  curl "http://localhost:8000/api/v1/workflow/status/your-job-id"
  sleep 10
done
```

## Use Cases

### 1. Content Marketing Campaign

**Scenario**: Create a complete marketing campaign for a new product.

```bash
# Step 1: Upload relevant documents
curl -X POST "http://localhost:8000/api/v1/documents/ingest/files" \
  -F "files=@product_brief.pdf" \
  -F "files=@competitor_analysis.docx" \
  -F "files=@brand_guidelines.pdf"

# Step 2: Submit comprehensive campaign request
curl -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a multi-channel marketing campaign including social media, email, and web content",
    "project_context": "New product launch in competitive market",
    "requirements": {
      "channels": ["Instagram", "LinkedIn", "Email", "Blog"],
      "campaign_duration": "4 weeks",
      "tone": "professional but approachable",
      "include_visuals": true,
      "call_to_action": "sign up for early access"
    },
    "priority": 9
  }'

# Step 3: Generate supporting media
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hero image for product launch campaign, modern and professional",
    "media_type": "image",
    "style": "modern corporate",
    "size": "1920x1080"
  }'
```

### 2. Research-Based Content Creation

**Scenario**: Create content based on uploaded research documents.

```bash
# Step 1: Upload research documents
curl -X POST "http://localhost:8000/api/v1/documents/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Recent study shows 85% increase in demand for sustainable products...",
      "Consumer behavior analysis reveals preference for transparent brands..."
    ],
    "metadata": [
      {"source": "research_study", "title": "Sustainability Trends 2024"},
      {"source": "consumer_analysis", "title": "Brand Trust Study"}
    ]
  }'

# Step 2: Use AI agent to create research-based content
curl -X POST "http://localhost:8000/api/v1/documents/query-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Write a blog post about sustainable technology trends, using our research data and include a compelling header image",
    "system_message": "You are an expert content writer who creates engaging, data-driven articles. Use the uploaded research to support your points and generate appropriate visuals."
  }'
```

### 3. Multimedia Presentation Creation

**Scenario**: Create a presentation with text, images, and audio.

```bash
# Step 1: Create presentation content
curl -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a 10-slide presentation about our company\'s impact on sustainability",
    "project_context": "Quarterly stakeholder meeting presentation",
    "requirements": {
      "slides": 10,
      "topics": ["company overview", "sustainability goals", "achievements", "future plans"],
      "tone": "professional and inspiring",
      "include_statistics": true
    },
    "priority": 7
  }'

# Step 2: Generate presentation images
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Infographic showing sustainability impact metrics and growth charts",
    "media_type": "image",
    "style": "infographic",
    "size": "1920x1080"
  }'

# Step 3: Generate narration audio
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Welcome to our quarterly sustainability update. Today we'll explore our progress toward our environmental goals...",
    "media_type": "tts",
    "voice": "professional",
    "format": "mp3"
  }'
```

## Best Practices

### Writing Effective Prompts

1. **Be Specific**: Include detailed requirements and context
   ```json
   {
     "task_description": "Create a LinkedIn post announcing our new feature",
     "requirements": {
       "tone": "professional but excited",
       "length": "150-200 words",
       "include_hashtags": true,
       "call_to_action": "visit our website"
     }
   }
   ```

2. **Provide Context**: Include relevant background information
   ```json
   {
     "project_context": "B2B SaaS company targeting enterprise clients in the finance sector"
   }
   ```

3. **Set Clear Expectations**: Define deliverables and success criteria
   ```json
   {
     "requirements": {
       "deliverables": ["headline", "body copy", "CTA button text"],
       "success_metrics": "engagement rate > 5%",
       "brand_guidelines": "follow company style guide v2.1"
     }
   }
   ```

### Document Management

1. **Organize Documents**: Use descriptive metadata
   ```json
   {
     "metadata": [
       {
         "source": "market_research",
         "title": "Q4 2024 Consumer Trends",
         "date": "2024-01-15",
         "category": "research",
         "tags": ["consumer behavior", "trends", "2024"]
       }
     ]
   }
   ```

2. **Regular Updates**: Keep your knowledge base current
   - Remove outdated information
   - Add new research and insights
   - Update product information

3. **Quality Control**: Ensure document quality
   - Use clear, well-formatted text
   - Include relevant context
   - Verify information accuracy

### Media Generation Tips

1. **Descriptive Prompts**: Be detailed in your media requests
   ```json
   {
     "prompt": "Modern office environment with diverse team collaborating on laptops, bright natural lighting, professional atmosphere, shot with DSLR camera"
   }
   ```

2. **Consistent Style**: Maintain brand consistency
   ```json
   {
     "style": "corporate professional",
     "size": "1920x1080",
     "additional_context": "follow brand guidelines with blue and green color scheme"
   }
   ```

3. **Format Considerations**: Choose appropriate formats
   - Images: Use high resolution for print, web-optimized for digital
   - Audio: MP3 for general use, WAV for professional production
   - Video: Consider platform requirements (Instagram vs YouTube)

## Troubleshooting

### Common Issues

1. **Job Stuck in "Pending"**
   - Check Celery workers: `curl http://localhost:8000/health`
   - Verify Redis connection
   - Check worker logs

2. **Poor Content Quality**
   - Provide more specific context
   - Upload relevant reference documents
   - Refine your requirements

3. **Media Generation Fails**
   - Check external MCP server status: `curl http://localhost:8000/api/v1/documents/external-servers`
   - Verify server configurations
   - Try simpler prompts

4. **Document Search Not Working**
   - Verify documents were ingested: `curl http://localhost:8000/api/v1/documents/stats`
   - Check search queries are specific enough
   - Ensure documents contain relevant content

### Getting Help

1. **API Documentation**: `http://localhost:8000/docs`
2. **Health Status**: `http://localhost:8000/health`
3. **System Logs**: Check application logs for detailed error messages

## API Integration

### Python Example

```python
import requests
import json
import time

class CuratedAgentClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def submit_workflow(self, task_description, project_context=None, requirements=None, priority=5):
        payload = {
            "task_description": task_description,
            "project_context": project_context,
            "requirements": requirements or {},
            "priority": priority
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/workflow/submit",
            json=payload
        )
        return response.json()
    
    def get_job_status(self, job_id):
        response = requests.get(
            f"{self.base_url}/api/v1/workflow/status/{job_id}"
        )
        return response.json()
    
    def wait_for_completion(self, job_id, timeout=300):
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"Job failed: {status.get('error_message')}")
            
            time.sleep(10)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")

# Usage example
client = CuratedAgentClient()

job = client.submit_workflow(
    task_description="Create a social media campaign for our new product",
    project_context="Tech startup launching innovative app",
    requirements={
        "platforms": ["Twitter", "LinkedIn"],
        "tone": "professional but engaging"
    }
)

print(f"Job submitted: {job['job_id']}")
result = client.wait_for_completion(job['job_id'])
print(f"Job completed: {result['result']}")
```

### JavaScript Example

```javascript
class CuratedAgentClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async submitWorkflow(taskDescription, projectContext = null, requirements = {}, priority = 5) {
        const response = await fetch(`${this.baseUrl}/api/v1/workflow/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_description: taskDescription,
                project_context: projectContext,
                requirements: requirements,
                priority: priority
            })
        });
        
        return await response.json();
    }

    async getJobStatus(jobId) {
        const response = await fetch(`${this.baseUrl}/api/v1/workflow/status/${jobId}`);
        return await response.json();
    }

    async waitForCompletion(jobId, timeout = 300000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const status = await this.getJobStatus(jobId);
            
            if (status.status === 'completed') {
                return status;
            } else if (status.status === 'failed') {
                throw new Error(`Job failed: ${status.error_message}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 10000));
        }
        
        throw new Error(`Job ${jobId} did not complete within ${timeout}ms`);
    }
}

// Usage example
const client = new CuratedAgentClient();

const job = await client.submitWorkflow(
    "Create email marketing content for our newsletter",
    "B2B SaaS company",
    {
        tone: "professional",
        length: "medium",
        include_cta: true
    }
);

console.log(`Job submitted: ${job.job_id}`);
const result = await client.waitForCompletion(job.job_id);
console.log(`Job completed: ${result.result}`);
```

This user guide provides comprehensive instructions for using all features of the Curated Agent system, from basic creative workflows to advanced multimedia generation and API integration.