#!/bin/bash

# Test runner script

echo "🧪 Running ABA Voice Agent Tests..."

# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
pytest tests/ \
    --verbose \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --color=yes

echo ""
echo "✅ Tests complete! Coverage report available in htmlcov/index.html"
