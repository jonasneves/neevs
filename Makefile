.PHONY: help install dev build start stop clean test logs

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Neevs Full Stack - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && go mod download
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✅ All dependencies installed$(NC)"

dev: ## Start development environment (all services)
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose up

dev-detached: ## Start development environment in background
	@echo "$(BLUE)Starting development environment (detached)...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Stack is running in background$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend:  http://localhost:3001$(NC)"

build: ## Build all services
	@echo "$(BLUE)Building backend...$(NC)"
	cd backend && go build -o backend .
	@echo "$(BLUE)Building frontend...$(NC)"
	cd frontend && npm run build
	@echo "$(GREEN)✅ Build complete$(NC)"

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✅ Docker images built$(NC)"

start: ## Start production stack with Docker
	@echo "$(BLUE)Starting production stack...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Stack started$(NC)"
	@make logs

stop: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ All services stopped$(NC)"

restart: stop start ## Restart all services

clean: ## Clean up containers, volumes, and build artifacts
	@echo "$(BLUE)Cleaning up...$(NC)"
	docker-compose down -v
	rm -f backend/backend
	rm -rf frontend/.next
	rm -rf frontend/out
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs only
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs only
	docker-compose logs -f frontend

logs-db: ## Show database logs only
	docker-compose logs -f postgres

test-health: ## Test backend health endpoint
	@echo "$(BLUE)Testing backend health...$(NC)"
	@curl -s http://localhost:3001/api/health | jq . || echo "$(YELLOW)Backend not responding$(NC)"

test-api: ## Run API tests
	@echo "$(BLUE)Testing API endpoints...$(NC)"
	@echo "\n$(GREEN)1. Health check:$(NC)"
	@curl -s http://localhost:3001/api/health | jq .
	@echo "\n$(GREEN)2. Creating test item:$(NC)"
	@curl -s -X POST http://localhost:3001/api/items \
		-H "Content-Type: application/json" \
		-d '{"title":"Test from Makefile","description":"Automated test"}' | jq .
	@echo "\n$(GREEN)3. Listing all items:$(NC)"
	@curl -s http://localhost:3001/api/items | jq .

db-shell: ## Connect to PostgreSQL shell
	@echo "$(BLUE)Connecting to database...$(NC)"
	@docker-compose exec postgres psql -U postgres -d neevs

status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps

dev-backend: ## Run backend only (local development)
	@echo "$(BLUE)Starting backend in development mode...$(NC)"
	cd backend && go run main.go

dev-frontend: ## Run frontend only (local development)
	@echo "$(BLUE)Starting frontend in development mode...$(NC)"
	cd frontend && npm run dev

setup-env: ## Create .env files from examples
	@echo "$(BLUE)Setting up environment files...$(NC)"
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "Created backend/.env"; fi
	@if [ ! -f frontend/.env.local ]; then cp frontend/.env.example frontend/.env.local; echo "Created frontend/.env.local"; fi
	@echo "$(GREEN)✅ Environment files ready$(NC)"

