#!/bin/bash

# Initial setup script
# Usage: ./scripts/setup.sh

set -e

echo "🎯 Setting up JobMet Backend..."

# Check prerequisites
echo "🔍 Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose not found."; exit 1; }

echo "✅ All prerequisites met"

# Create environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp docker/.env.example .env
    echo "⚠️  Please edit .env file with your configuration"
    exit 0
fi

# Create required directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p backups

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for database
echo "⏳ Waiting for database..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T backend alembic upgrade head

# Health check
echo "🏥 Running health check..."
sleep 5

HEALTH_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$HEALTH_STATUS" == "healthy" ]; then
    echo "✅ Setup successful!"
else
    echo "⚠️  Health check returned: $HEALTH_STATUS"
fi

echo ""
echo "🎉 JobMet Backend is ready!"
echo ""
echo "📊 Services:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
