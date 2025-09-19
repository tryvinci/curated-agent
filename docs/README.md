# Curated Agent Documentation

Welcome to the comprehensive documentation for the Curated Agent system - a powerful AI-driven creative workflow automation platform.

## 📋 Table of Contents

### 🚀 Getting Started
- [Quick Start Guide](../README.md#quick-start) - Get up and running in 5 minutes
- [System Requirements](deployment/README.md#prerequisites) - Hardware and software requirements
- [Installation Guide](deployment/README.md#quick-start-local-development) - Step-by-step installation

### 📚 Core Documentation

#### 🏗️ Architecture
- [System Architecture](architecture/README.md) - Overall system design and components
- [Data Flow](architecture/README.md#data-flow) - How data moves through the system
- [Scalability](architecture/README.md#scalability-considerations) - Scaling considerations

#### 🔧 API Reference
- [Complete API Documentation](api/README.md) - All endpoints and examples
- [Creative Workflow API](api/README.md#creative-workflow-api) - AI workflow automation
- [Document Processing API](api/README.md#document-processing-api) - Knowledge base management
- [MCP Tools API](api/README.md#mcp-tools-api) - Tool management and execution
- [Observability API](api/README.md#observability-api) - Monitoring and feedback

#### 🚢 Deployment
- [Deployment Guide](deployment/README.md) - Complete deployment instructions
- [Docker Setup](deployment/README.md#quick-start-local-development) - Containerized deployment
- [Kubernetes](deployment/README.md#kubernetes-deployment) - Production orchestration
- [Environment Configuration](deployment/README.md#environment-configuration) - Configuration management

#### 👥 User Guide
- [User Guide](guides/README.md) - How to use the system
- [Best Practices](guides/README.md#best-practices) - Optimization tips
- [Use Cases](guides/README.md#use-cases) - Real-world examples
- [Troubleshooting](guides/README.md#troubleshooting) - Common issues and solutions

### 🔍 Specialized Features

#### 🤖 AI and Workflow
- [CrewAI Integration](guides/README.md#creative-workflow-automation) - Multi-agent AI workflows
- [Anthropic Claude](guides/README.md#enhanced-creative-workflow) - LLM integration
- [Prompt Engineering](guides/README.md#writing-effective-prompts) - Creating effective prompts

#### 🛠️ Tools and Extensions
- [MCP Protocol](guides/README.md#mcp-tools-integration) - Model Context Protocol
- [External MCP Servers](guides/README.md#media-generation) - Remote tool integration
- [LlamaIndex](guides/README.md#document-processing-and-knowledge-base) - Document processing

#### 📊 Monitoring and Observability
- [HoneyHive Integration](guides/honeyhive-integration.md) - AI observability platform
- [Performance Monitoring](guides/honeyhive-integration.md#monitoring-workflows) - Tracking performance
- [Cost Optimization](guides/honeyhive-integration.md#cost-optimization) - Managing AI costs

#### 📁 Document Management
- [Document Ingestion](guides/README.md#document-processing-and-knowledge-base) - Adding documents
- [Semantic Search](guides/README.md#search-documents) - Intelligent search
- [Knowledge Base](guides/README.md#document-management) - Best practices

#### 🎨 Media Generation
- [Image Generation](guides/README.md#generate-images) - AI image creation
- [Text-to-Speech](guides/README.md#generate-text-to-speech) - Voice synthesis
- [Video Generation](guides/README.md#generate-videos) - Video creation

## 🌟 Key Features

### 🤖 Multi-Agent AI Workflows
- **Creative Director**: Strategic planning and oversight
- **Content Creator**: Content generation with multimedia capabilities
- **Quality Reviewer**: Quality assurance and refinement

### 📄 Intelligent Document Processing
- Support for PDF, DOCX, and text files
- Semantic search and retrieval
- Knowledge base integration with AI agents

### 🛠️ Extensible Tool System
- Model Context Protocol (MCP) integration
- External server connectivity
- Custom tool development support

### 🎯 Media Generation
- AI-powered image creation
- Text-to-speech synthesis
- Video generation capabilities

### 📊 Comprehensive Observability
- Full workflow tracking with HoneyHive
- Performance monitoring and optimization
- Cost tracking and analysis
- User feedback collection

### 🏗️ Production-Ready Architecture
- Docker containerization
- Kubernetes support
- Horizontal scaling capabilities
- Health monitoring and alerting

## 🏃‍♂️ Quick Navigation

### For Developers
1. [Architecture Overview](architecture/README.md) - Understand the system
2. [API Documentation](api/README.md) - Integrate with the API
3. [Deployment Guide](deployment/README.md) - Deploy the system

### For End Users
1. [User Guide](guides/README.md) - Learn to use the system
2. [Best Practices](guides/README.md#best-practices) - Optimize your workflows
3. [Use Cases](guides/README.md#use-cases) - Real-world examples

### For System Administrators
1. [Deployment Guide](deployment/README.md) - Production deployment
2. [Monitoring](guides/honeyhive-integration.md) - System observability
3. [Troubleshooting](guides/README.md#troubleshooting) - Issue resolution

## 📈 Common Workflows

### 1. Content Marketing Campaign
```bash
# Upload brand guidelines and research
curl -X POST "http://localhost:8000/api/v1/documents/ingest/files" -F "files=@brand_guide.pdf"

# Submit campaign workflow
curl -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -d '{"task_description": "Create comprehensive marketing campaign for product launch"}'

# Generate supporting media
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -d '{"prompt": "Product hero image", "media_type": "image"}'
```

### 2. Document-Based Content Creation
```bash
# Ingest research documents
curl -X POST "http://localhost:8000/api/v1/documents/ingest/text" \
  -d '{"texts": ["Research data..."], "metadata": [{"source": "study"}]}'

# Create content using AI agent with tools
curl -X POST "http://localhost:8000/api/v1/documents/query-with-tools" \
  -d '{"query": "Create blog post based on research data with supporting visuals"}'
```

### 3. Multimedia Presentation
```bash
# Generate presentation content
curl -X POST "http://localhost:8000/api/v1/workflow/submit" \
  -d '{"task_description": "Create 10-slide presentation on company achievements"}'

# Generate supporting media
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -d '{"prompt": "Infographic of company metrics", "media_type": "image"}'

# Generate narration
curl -X POST "http://localhost:8000/api/v1/documents/generate-media" \
  -d '{"prompt": "Welcome to our quarterly review...", "media_type": "tts"}'
```

## 🔧 Configuration Examples

### Basic Setup
```bash
# .env file
ANTHROPIC_API_KEY=your_api_key_here
REDIS_HOST=localhost
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Production Setup
```bash
# .env file
ANTHROPIC_API_KEY=your_production_key
REDIS_HOST=redis.production.com
REDIS_PASSWORD=secure_password
HONEYHIVE_API_KEY=your_honeyhive_key
MCP_MEDIA_SERVER_URL=https://media.yourcompany.com
```

## 🆘 Support and Resources

### Documentation
- **API Reference**: Complete endpoint documentation with examples
- **Architecture Guide**: System design and component interaction
- **User Guide**: Step-by-step usage instructions
- **Deployment Guide**: Production deployment best practices

### Community and Support
- GitHub Issues: Report bugs and request features
- Documentation: Comprehensive guides and examples
- API Explorer: Interactive API testing at `/docs`

### Monitoring and Debugging
- Health Check: `GET /health` - System status
- Observability: `GET /api/v1/observability/health` - Monitoring status
- API Documentation: `GET /docs` - Interactive API explorer
- Logs: Application and component logs for debugging

## 🔄 Updates and Changelog

### Latest Features
- **HoneyHive Integration**: Complete AI observability and monitoring
- **External MCP Servers**: Distributed media generation services
- **Enhanced Documentation**: Comprehensive guides and examples
- **Performance Optimizations**: Improved response times and scalability

### Upcoming Features
- Advanced workflow templates
- Enhanced media generation options
- Real-time collaboration features
- Extended analytics and reporting

---

## 📖 Document Structure

```
docs/
├── api/                    # API documentation
│   └── README.md          # Complete API reference
├── architecture/          # System architecture
│   └── README.md          # Architecture overview
├── deployment/            # Deployment guides
│   └── README.md          # Deployment instructions
├── guides/               # User guides
│   ├── README.md         # Main user guide
│   └── honeyhive-integration.md  # Observability guide
└── README.md            # This file - documentation index
```

This documentation is designed to provide comprehensive coverage of the Curated Agent system, from quick start guides to detailed technical documentation. Choose your starting point based on your role and needs.