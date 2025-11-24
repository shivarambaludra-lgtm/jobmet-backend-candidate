#!/bin/bash

# Database backup script
# Run daily via cron: 0 2 * * * /app/scripts/backup.sh

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)

# Database credentials (from environment)
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-jobmet}
DB_USER=${DB_USER:-jobmet}
DB_PASSWORD=${DB_PASSWORD}

# Create backup directory
mkdir -p $BACKUP_DIR

echo "🔄 Starting backup at $(date)"

# PostgreSQL backup
echo "📦 Backing up PostgreSQL..."
PGPASSWORD=$DB_PASSWORD pg_dump \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -F c \
    -b \
    -v \
    -f "${BACKUP_DIR}/postgres_${DATE}.dump" \
    $DB_NAME

# Compress backup
gzip "${BACKUP_DIR}/postgres_${DATE}.dump"

# Redis backup
echo "📦 Backing up Redis..."
redis-cli --rdb "${BACKUP_DIR}/redis_${DATE}.rdb"
gzip "${BACKUP_DIR}/redis_${DATE}.rdb"

# Delete old backups
echo "🗑️  Cleaning up old backups..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup completed at $(date)"
echo "📂 Backup location: $BACKUP_DIR"
