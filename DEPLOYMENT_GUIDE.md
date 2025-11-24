# JobMet Backend - Deployment Guide

## Prerequisites

### Required Software
- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **Docker Compose** v2.0+
- **Git**
- **Python 3.11+** (for local development)

### Required Accounts/Keys
- OpenAI API Key
- Sentry DSN (optional, for error tracking)
- SMTP credentials (for email alerts)

---

## Quick Start (Windows)

### 1. Clone Repository
```powershell
git clone <your-repo-url>
cd jobmet-backend-candidate
```

### 2. Configure Environment
```powershell
# Copy environment template
Copy-Item docker\.env.example .env

# Edit .env with your values
notepad .env
```

**Required Environment Variables:**
```bash
# Database
POSTGRES_PASSWORD=your_strong_password_here
DATABASE_URL=postgresql://jobmet:your_password@db:5432/jobmet

# Redis
REDIS_URL=redis://redis:6379/0

# Neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_URI=bolt://neo4j:7687

# Application
SECRET_KEY=your_secret_key_min_32_characters
ENVIRONMENT=production

# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-your_openai_api_key_here

# Monitoring (Optional)
SENTRY_DSN=https://your_sentry_dsn_here

# Email (Optional - for saved search alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@jobmet.ai
```

### 3. Run Setup Script
```powershell
# PowerShell
.\scripts\setup.ps1
```

### 4. Verify Installation
```powershell
# Check health
curl http://localhost:8000/health

# View API docs
Start-Process "http://localhost:8000/docs"
```

---

## Quick Start (Linux/Mac)

### 1. Clone and Configure
```bash
git clone <your-repo-url>
cd jobmet-backend-candidate
cp docker/.env.example .env
nano .env  # Edit with your values
```

### 2. Run Setup
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Verify
```bash
curl http://localhost:8000/health
```

---

## Manual Setup (All Platforms)

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Wait for Services
```bash
# Wait 10-15 seconds for all services to be ready
docker-compose ps
```

### 3. Run Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 4. Check Logs
```bash
docker-compose logs -f backend
```

---

## Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| PostgreSQL | localhost:5432 | jobmet / (from .env) |
| Redis | localhost:6379 | - |
| Neo4j Browser | http://localhost:7474 | neo4j / (from .env) |

---

## Common Commands

### Start/Stop Services
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
```

### Database Operations
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Database shell
docker-compose exec db psql -U jobmet -d jobmet
```

### Celery Operations
```bash
# View Celery worker logs
docker-compose logs -f celery-worker

# View Celery beat logs
docker-compose logs -f celery-beat

# Restart workers
docker-compose restart celery-worker celery-beat
```

---

## Testing

### Run Tests
```bash
# All tests
docker-compose exec backend pytest tests/ -v

# With coverage
docker-compose exec backend pytest tests/ -v --cov=app
```

### Load Testing
```bash
# Install locust locally
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000

# Headless mode
locust -f tests/load_test.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 5m --headless
```

---

## Monitoring

### Health Checks
```bash
# Basic health
curl http://localhost:8000/health

# Detailed health (requires admin auth)
curl http://localhost:8000/api/v1/monitoring/health/detailed
```

### System Metrics
```bash
# Requires admin authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/monitoring/metrics
```

### View Logs
```bash
# Structured JSON logs
docker-compose logs backend | tail -100

# Real-time logs
docker-compose logs -f backend
```

---

## Troubleshooting

### Services Won't Start
```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues
```bash
# Check database is healthy
docker-compose exec db pg_isready -U jobmet

# Check connection from backend
docker-compose exec backend python -c "from app.core.database import engine; print(engine.connect())"
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Port Already in Use
```powershell
# Windows - Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# ports:
#   - "8001:8000"  # Use 8001 instead
```

### Clear Everything and Start Fresh
```bash
# WARNING: This deletes all data
docker-compose down -v
docker system prune -f
docker volume prune -f

# Then run setup again
```

---

## Production Deployment

### Pre-Deployment Checklist
- [ ] Configure strong passwords in `.env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure Sentry DSN
- [ ] Set up SSL certificates
- [ ] Configure SMTP for emails
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts

### Deploy to Server
```bash
# SSH to server
ssh user@your-server.com

# Clone repository
git clone <repo-url>
cd jobmet-backend

# Configure environment
cp docker/.env.example .env
nano .env

# Run setup
./scripts/setup.sh

# Or deploy with script
./scripts/deploy.sh
```

### SSL/HTTPS Setup
1. Install certbot
2. Get certificates:
   ```bash
   certbot certonly --webroot -w /var/www/certbot \
     -d yourdomain.com -d www.yourdomain.com
   ```
3. Update `docker/nginx.conf` with certificate paths
4. Restart nginx:
   ```bash
   docker-compose restart nginx
   ```

---

## Backup & Recovery

### Manual Backup
```bash
# Run backup script
./scripts/backup.sh
```

### Automated Backups
```bash
# Add to crontab (daily at 2 AM)
0 2 * * * /app/jobmet-backend/scripts/backup.sh
```

### Restore from Backup
```bash
# Stop services
docker-compose down

# Restore PostgreSQL
gunzip backups/postgres_YYYYMMDD_HHMMSS.dump.gz
docker-compose exec -T db pg_restore -U jobmet -d jobmet < backups/postgres_YYYYMMDD_HHMMSS.dump

# Restart services
docker-compose up -d
```

---

## Performance Optimization

### Scaling Workers
```yaml
# In docker-compose.yml
celery-worker:
  deploy:
    replicas: 4  # Run 4 worker instances
```

### Database Optimization
```bash
# Run optimization script
docker-compose exec db psql -U jobmet -d jobmet -f scripts/optimize_db.sql
```

### Cache Tuning
- Adjust TTL values in `app/core/cache.py`
- Monitor cache hit rates
- Increase Redis memory if needed

---

## Support

- **Documentation**: See `WEEK_9_10_COMPLETE.md`
- **Issues**: Check logs first, then create GitHub issue
- **Health Check**: http://localhost:8000/health

---

**Your JobMet backend is now ready for production! 🚀**
