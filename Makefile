.PHONY: help setup start stop restart logs test clean

help:
	@echo "JobMet Backend - Available Commands"
	@echo ""
	@echo "  make setup      - Initial setup"
	@echo "  make start      - Start all services"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean up containers"
	@echo ""

setup:
	@echo "🎯 Setting up JobMet Backend..."
	@docker-compose up -d
	@docker-compose exec backend alembic upgrade head
	@echo "✅ Setup complete!"

start:
	@docker-compose up -d
	@echo "✅ Services started"

stop:
	@docker-compose down
	@echo "✅ Services stopped"

restart:
	@docker-compose restart
	@echo "✅ Services restarted"

logs:
	@docker-compose logs -f --tail=100

test:
	@docker-compose exec backend pytest tests/ -v --cov=app

clean:
	@docker-compose down -v
	@docker system prune -f
	@echo "✅ Cleaned up"

migrate:
	@docker-compose exec backend alembic upgrade head

health:
	@curl -s http://localhost:8000/health | jq
