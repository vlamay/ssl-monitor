# SSL Monitor Pro - Development Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate docs

# Default target
help: ## Show this help message
	@echo "SSL Monitor Pro - Development Commands"
	@echo "======================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make dev          # Start development environment"
	@echo "  make test         # Run all tests"
	@echo "  make lint         # Run linting and formatting"
	@echo "  make docker-up    # Start Docker services"

# =============================================================================
# INSTALLATION AND SETUP
# =============================================================================

install: ## Install all dependencies
	@echo "Installing dependencies..."
	@cd backend && python -m venv venv
	@cd backend && . venv/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt
	@cd frontend-modern && npm install
	@echo "✅ Dependencies installed successfully"

install-backend: ## Install backend dependencies only
	@echo "Installing backend dependencies..."
	@cd backend && python -m venv venv
	@cd backend && . venv/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt
	@echo "✅ Backend dependencies installed"

install-frontend: ## Install frontend dependencies only
	@echo "Installing frontend dependencies..."
	@cd frontend-modern && npm install
	@echo "✅ Frontend dependencies installed"

setup: ## Initial project setup
	@echo "Setting up SSL Monitor Pro..."
	@cp env.example .env
	@echo "✅ Environment file created (.env)"
	@echo "📝 Please edit .env file with your configuration"
	@make install
	@make migrate
	@echo "✅ Setup complete!"

# =============================================================================
# DEVELOPMENT
# =============================================================================

dev: ## Start development environment
	@echo "Starting development environment..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@docker-compose -f docker-compose.dev.yml up

dev-backend: ## Start backend development server
	@echo "Starting backend development server..."
	@cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	@echo "Starting frontend development server..."
	@cd frontend-modern && npm run dev

dev-celery: ## Start Celery worker and beat
	@echo "Starting Celery services..."
	@cd backend && . venv/bin/activate && celery -A celery_worker worker --loglevel=info &
	@cd backend && . venv/bin/activate && celery -A celery_worker beat --loglevel=info

# =============================================================================
# TESTING
# =============================================================================

test: ## Run all tests
	@echo "Running all tests..."
	@make test-backend
	@make test-frontend

test-backend: ## Run backend tests
	@echo "Running backend tests..."
	@cd backend && . venv/bin/activate && pytest -v --cov=app --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests
	@echo "Running frontend tests..."
	@cd frontend-modern && npm test

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	@cd backend && . venv/bin/activate && pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	@echo "Running E2E tests..."
	@cd frontend-modern && npm run test:e2e

test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	@cd backend && . venv/bin/activate && pytest-watch

test-coverage: ## Generate test coverage report
	@echo "Generating coverage report..."
	@cd backend && . venv/bin/activate && pytest --cov=app --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in backend/htmlcov/index.html"

# =============================================================================
# CODE QUALITY
# =============================================================================

lint: ## Run linting and formatting
	@echo "Running code quality checks..."
	@make lint-backend
	@make lint-frontend

lint-backend: ## Run backend linting
	@echo "Linting backend code..."
	@cd backend && . venv/bin/activate && flake8 app/ tests/
	@cd backend && . venv/bin/activate && black --check app/ tests/
	@cd backend && . venv/bin/activate && isort --check-only app/ tests/
	@cd backend && . venv/bin/activate && mypy app/

lint-frontend: ## Run frontend linting
	@echo "Linting frontend code..."
	@cd frontend-modern && npm run lint

format: ## Format code
	@echo "Formatting code..."
	@make format-backend
	@make format-frontend

format-backend: ## Format backend code
	@echo "Formatting backend code..."
	@cd backend && . venv/bin/activate && black app/ tests/
	@cd backend && . venv/bin/activate && isort app/ tests/

format-frontend: ## Format frontend code
	@echo "Formatting frontend code..."
	@cd frontend-modern && npm run format

security: ## Run security checks
	@echo "Running security checks..."
	@cd backend && . venv/bin/activate && bandit -r app/
	@cd backend && . venv/bin/activate && safety check
	@cd frontend-modern && npm audit

# =============================================================================
# DATABASE
# =============================================================================

migrate: ## Run database migrations
	@echo "Running database migrations..."
	@cd backend && . venv/bin/activate && python app/migrate.py

migrate-create: ## Create new migration
	@echo "Creating new migration..."
	@cd backend && . venv/bin/activate && alembic revision --autogenerate -m "$(message)"

migrate-upgrade: ## Upgrade database to latest migration
	@echo "Upgrading database..."
	@cd backend && . venv/bin/activate && alembic upgrade head

migrate-downgrade: ## Downgrade database by one migration
	@echo "Downgrading database..."
	@cd backend && . venv/bin/activate && alembic downgrade -1

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		echo "Resetting database..."; \
		cd backend && . venv/bin/activate && python app/migrate.py --reset; \
	fi

# =============================================================================
# DOCKER
# =============================================================================

docker-build: ## Build Docker images
	@echo "Building Docker images..."
	@docker-compose -f docker-compose.dev.yml build

docker-up: ## Start Docker services
	@echo "Starting Docker services..."
	@docker-compose -f docker-compose.dev.yml up -d

docker-down: ## Stop Docker services
	@echo "Stopping Docker services..."
	@docker-compose -f docker-compose.dev.yml down

docker-logs: ## View Docker logs
	@echo "Viewing Docker logs..."
	@docker-compose -f docker-compose.dev.yml logs -f

docker-clean: ## Clean Docker containers and images
	@echo "Cleaning Docker resources..."
	@docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	@docker system prune -f

docker-shell-backend: ## Open shell in backend container
	@docker-compose -f docker-compose.dev.yml exec backend /bin/bash

docker-shell-frontend: ## Open shell in frontend container
	@docker-compose -f docker-compose.dev.yml exec frontend /bin/sh

# =============================================================================
# PRODUCTION
# =============================================================================

build-prod: ## Build production Docker images
	@echo "Building production images..."
	@docker-compose -f docker-compose.yml build

deploy-staging: ## Deploy to staging environment
	@echo "Deploying to staging..."
	@echo "This would deploy to staging environment"

deploy-prod: ## Deploy to production environment
	@echo "Deploying to production..."
	@echo "This would deploy to production environment"

# =============================================================================
# DOCUMENTATION
# =============================================================================

docs: ## Generate documentation
	@echo "Generating documentation..."
	@cd backend && . venv/bin/activate && sphinx-build -b html docs/ docs/_build/html
	@echo "📚 Documentation generated in backend/docs/_build/html"

docs-serve: ## Serve documentation locally
	@echo "Serving documentation..."
	@cd backend/docs/_build/html && python -m http.server 8001

# =============================================================================
# UTILITIES
# =============================================================================

clean: ## Clean temporary files
	@echo "Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name "node_modules" -exec rm -rf {} +
	@find . -type f -name "package-lock.json" -delete
	@echo "✅ Cleanup complete"

logs: ## View application logs
	@echo "Viewing application logs..."
	@docker-compose -f docker-compose.dev.yml logs -f backend frontend

status: ## Check service status
	@echo "Checking service status..."
	@docker-compose -f docker-compose.dev.yml ps

health: ## Check service health
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Backend not responding"
	@curl -f http://localhost:3000 || echo "Frontend not responding"

# =============================================================================
# DEVELOPMENT TOOLS
# =============================================================================

tools: ## Start development tools (pgAdmin, Redis Commander, Mailhog)
	@echo "Starting development tools..."
	@docker-compose -f docker-compose.dev.yml --profile tools up -d
	@echo "🔧 Development tools started:"
	@echo "  pgAdmin: http://localhost:5050"
	@echo "  Redis Commander: http://localhost:8081"
	@echo "  Mailhog: http://localhost:8025"

shell-backend: ## Open Python shell with app context
	@echo "Opening Python shell..."
	@cd backend && . venv/bin/activate && python -c "from app.main import app; import IPython; IPython.embed()"

shell-db: ## Open database shell
	@echo "Opening database shell..."
	@docker-compose -f docker-compose.dev.yml exec postgres psql -U sslmonitor_user -d sslmonitor_dev

shell-redis: ## Open Redis shell
	@echo "Opening Redis shell..."
	@docker-compose -f docker-compose.dev.yml exec redis redis-cli

# =============================================================================
# MONITORING AND DEBUGGING
# =============================================================================

monitor: ## Start monitoring dashboard
	@echo "Starting monitoring..."
	@echo "This would start monitoring dashboard"

debug-backend: ## Start backend in debug mode
	@echo "Starting backend in debug mode..."
	@cd backend && . venv/bin/activate && python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn app.main:app --reload

profile: ## Profile backend performance
	@echo "Profiling backend performance..."
	@cd backend && . venv/bin/activate && python -m cProfile -o profile.stats app/main.py

# =============================================================================
# BACKUP AND RESTORE
# =============================================================================

backup: ## Backup database
	@echo "Creating database backup..."
	@docker-compose -f docker-compose.dev.yml exec postgres pg_dump -U sslmonitor_user sslmonitor_dev > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created"

restore: ## Restore database from backup
	@echo "Restoring database..."
	@echo "Usage: make restore BACKUP_FILE=backup_20250101_120000.sql"
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Please specify BACKUP_FILE"; \
		exit 1; \
	fi
	@docker-compose -f docker-compose.dev.yml exec -T postgres psql -U sslmonitor_user -d sslmonitor_dev < $(BACKUP_FILE)
	@echo "✅ Database restored"

# =============================================================================
# GIT HELPERS
# =============================================================================

git-hooks: ## Install git hooks
	@echo "Installing git hooks..."
	@cd backend && . venv/bin/activate && pre-commit install
	@echo "✅ Git hooks installed"

git-clean: ## Clean git repository
	@echo "Cleaning git repository..."
	@git clean -fd
	@git reset --hard HEAD
	@echo "✅ Git repository cleaned"

# =============================================================================
# QUICK COMMANDS
# =============================================================================

quick-start: ## Quick start development environment
	@echo "🚀 Quick starting SSL Monitor Pro..."
	@make install
	@make docker-up
	@make migrate
	@echo "✅ SSL Monitor Pro is ready!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

quick-test: ## Quick test run
	@echo "🧪 Running quick tests..."
	@make lint-backend
	@make test-backend
	@echo "✅ Quick tests completed"

quick-deploy: ## Quick deployment check
	@echo "🚀 Quick deployment check..."
	@make lint
	@make test
	@make security
	@echo "✅ Ready for deployment"

# =============================================================================
# HELPERS
# =============================================================================

check-deps: ## Check if all dependencies are installed
	@echo "Checking dependencies..."
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose not found"; exit 1; }
	@echo "✅ All dependencies found"

version: ## Show version information
	@echo "SSL Monitor Pro - Version Information"
	@echo "===================================="
	@echo "Python: $(shell python3 --version)"
	@echo "Node.js: $(shell node --version)"
	@echo "Docker: $(shell docker --version)"
	@echo "Docker Compose: $(shell docker-compose --version)"

# =============================================================================
# CUSTOM TARGETS
# =============================================================================

# Add custom targets here
# Example:
# my-custom-target: ## Description of custom target
#	@echo "Running custom target..."
#	@command-to-run
