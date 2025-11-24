#!/bin/bash

# Production deployment script
# Usage: ./scripts/deploy.sh

set -e

echo "🚀 Deploying to production..."

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose run --rm backend alembic upgrade head

# Deploy services with rolling update
echo "🔄 Deploying services..."
docker-compose up -d --no-deps backend
docker-compose up -d --no-deps celery-worker
docker-compose up -d --no-deps celery-beat

# Health check
echo "🏥 Running health check..."
sleep 10

HEALTH_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "❌ Health check failed!"
    exit 1
fi

# Clean up
echo "🧹 Cleaning up..."
docker image prune -f

echo "✅ Deployment successful!"
echo "🌐 Backend: http://localhost:8000"
