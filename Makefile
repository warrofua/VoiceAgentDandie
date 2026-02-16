.PHONY: help install dev test clean seed demo docs

help:
	@echo "ABA Voice Agent - Available Commands"
	@echo "===================================="
	@echo "make install    - Install dependencies"
	@echo "make dev        - Run development server"
	@echo "make test       - Run test suite"
	@echo "make seed       - Seed database with sample data"
	@echo "make demo       - Run demo conversation"
	@echo "make clean      - Clean temporary files"
	@echo "make lint       - Run code linting"
	@echo "make format     - Format code with black"
	@echo "make docs       - Open documentation"

install:
	@echo "Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

dev:
	@echo "Starting development server..."
	./scripts/run_dev.sh

test:
	@echo "Running tests..."
	./scripts/test.sh

seed:
	@echo "Seeding database..."
	python scripts/seed_data.py

demo:
	@echo "Running demo conversation..."
	python examples/demo_conversation.py

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf temp_audio/*.mp3 temp_audio/*.wav 2>/dev/null || true
	@echo "✅ Cleaned!"

lint:
	@echo "Running linters..."
	flake8 src/ tests/ --max-line-length=100
	mypy src/ --ignore-missing-imports

format:
	@echo "Formatting code..."
	black src/ tests/ examples/ scripts/

docs:
	@echo "Opening documentation..."
	@echo "📖 README.md - Main documentation"
	@echo "🚀 QUICKSTART.md - Quick setup guide"
	@echo "🏗️  docs/ARCHITECTURE.md - System architecture"
	@echo "🚢 docs/DEPLOYMENT.md - Deployment guide"
	open README.md || xdg-open README.md || start README.md

setup: install
	@echo "Setting up project..."
	cp .env.example .env
	mkdir -p temp_audio logs
	@echo "✅ Project setup complete!"
	@echo "⚠️  Don't forget to edit .env with your API keys!"

check-env:
	@echo "Checking environment..."
	@test -f .env || (echo "❌ .env file not found! Run 'make setup'" && exit 1)
	@test -n "$$OPENAI_API_KEY" || (echo "⚠️  OPENAI_API_KEY not set in .env" && exit 1)
	@echo "✅ Environment configured!"

all: install seed dev
