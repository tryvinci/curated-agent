#!/bin/bash

echo "🚀 Starting Curated Agent Development Environment"

# Check if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "📦 Docker Compose found - using containerized environment"
    echo "Starting services..."
    docker-compose up -d
    echo "✅ Services started!"
    echo ""
    echo "🔗 API Available at: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop services: docker-compose down"
else
    echo "⚠️  Docker Compose not found - using local development"
    echo "Make sure you have Redis running locally on port 6379"
    echo ""
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
    echo "Starting FastAPI server..."
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi