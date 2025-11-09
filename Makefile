.PHONY: start stop restart help

# Default target
help:
	@echo "Audio Transcription Service - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make start    - Start all Docker Compose services"
	@echo "  make stop     - Stop all Docker Compose services"
	@echo "  make restart  - Restart all Docker Compose services"
	@echo "  make help     - Show this help message"

# Start all services
start:
	@echo "Starting Docker Compose services..."
	docker compose up -d
	@echo "Services started successfully!"
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo ""
	@echo "Services status:"
	@docker compose ps
	@echo ""
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Stop all services
stop:
	@echo "Stopping Docker Compose services..."
	docker compose down
	@echo "Services stopped successfully!"

# Restart all services (calls stop then start)
restart: stop start
