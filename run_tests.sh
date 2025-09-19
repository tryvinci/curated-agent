#!/bin/bash

echo "🧪 Running Tests for Curated Agent"

# Install test dependencies
echo "Installing test dependencies..."
pip install pytest pytest-asyncio httpx

# Run the tests
echo "Running API tests..."
python -m pytest tests/ -v

echo "✅ Tests completed!"