# Brandwise Platform — Makefile for common commands

.PHONY: help up down build logs migrate migrate-down shell test lint format clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services (db, redis, minio, backend, worker)
	docker compose up -d

down: ## Stop and remove all services
	docker compose down

build: ## Build backend and worker images
	docker compose build

logs: ## Follow backend logs
	docker compose logs -f backend

worker-logs: ## Follow worker logs
	docker compose logs -f worker

db-logs: ## Follow database logs
	docker compose logs -f db

migrate: ## Run Alembic migrations to head
	docker compose exec backend alembic upgrade head

migrate-down: ## Downgrade one migration
	docker compose exec backend alembic downgrade -1

migrate-status: ## Show current migration status
	docker compose exec backend alembic current

migrate-history: ## Show migration history
	docker compose exec backend alembic history

makemigrations: ## Create a new Alembic migration (usage: make makemigrations m="message")
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

shell: ## Open a shell in the backend container
	docker compose exec backend sh

test: ## Run the test suite
	docker compose exec backend pytest

test-cov: ## Run tests with coverage
	docker compose exec backend pytest --cov=app --cov-report=term-missing

lint: ## Run ruff linter
	docker compose exec backend ruff check .

format: ## Format code with ruff
	docker compose exec backend ruff format .

typecheck: ## Run mypy type checker
	docker compose exec backend mypy app

clean: ## Remove containers, volumes, and images
	docker compose down -v --rmi all

install-deps: ## Install Python dependencies locally
	pip install -r backend/requirements.txt
