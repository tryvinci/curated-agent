#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt

echo "Dependencies installed successfully!"

# Test imports
echo "Testing imports..."
python -c "
import app.main
import app.celery_app
import app.services.redis_service
import app.services.creative_workflow
import app.tasks.creative_workflow
import app.models.schemas
print('All imports successful!')
"

echo "Basic validation complete!"