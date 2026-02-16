#!/bin/bash

# Development startup script

echo "🚀 Starting ABA Voice Agent Development Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your actual credentials before running."
    exit 1
fi

# Create temp directories
mkdir -p temp_audio
mkdir -p logs

# Check if database exists
echo "Checking database..."
python -c "from src.database.connection import engine; from src.models.database_models import Base; Base.metadata.create_all(engine)" 2>/dev/null

# Start the server
echo "Starting FastAPI server..."
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
