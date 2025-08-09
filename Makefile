.PHONY: help install install-dev start-backend start-frontend start-all test test-backend test-frontend lint format clean docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

install-dev: ## Install development dependencies
	@echo "Installing backend dev dependencies..."
	cd backend && pip install -e ".[dev]"
	@echo "Installing frontend dev dependencies..."
	cd frontend && npm install --include=dev

# Development server targets
start-backend: ## Start backend development server
	cd backend && python src/main.py

start-frontend: ## Start frontend development server
	cd frontend && npm run dev

start-all: ## Start all services with Docker Compose
	docker-compose up -d

# Testing targets
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && pytest

test-frontend: ## Run frontend tests
	cd frontend && npm test

# Code quality targets
lint: ## Run linting for all code
	cd backend && ruff check src/
	cd frontend && npm run lint

format: ## Format all code
	cd backend && black src/ && ruff check --fix src/
	cd frontend && npm run format

# Database targets
migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-create: ## Create new migration
	cd backend && alembic revision --autogenerate -m "$(name)"

# Docker targets
docker-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-build: ## Build Docker images
	docker-compose build

docker-logs: ## Show Docker logs
	docker-compose logs -f

# Utility targets
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	cd frontend && rm -rf node_modules/.cache

setup-env: ## Setup environment files
	cp backend/.env.example backend/.env
	@echo "Environment files created. Please update them with your configuration."

# Development workflow
dev-setup: install-dev setup-env ## Complete development setup
	@echo "Development setup complete!"
	@echo "Next steps:"
	@echo "1. Update backend/.env with your configuration"
	@echo "2. Run 'make start-all' to start all services"
	@echo "3. Visit http://localhost:3000 for frontend"
	@echo "4. Visit http://localhost:8000/docs for API documentation"

# Production targets
build-prod: ## Build production images
	docker-compose -f docker-compose.prod.yml build

deploy-prod: ## Deploy to production
	docker-compose -f docker-compose.prod.yml up -d
