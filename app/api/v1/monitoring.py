from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
import psutil
from app.core.cache import redis_client
from datetime import datetime

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/metrics")
async def get_system_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system metrics (admin only)"""
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Database health
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
        db_connection_count = db.execute(
            text("SELECT count(*) FROM pg_stat_activity")
        ).scalar()
    except Exception as e:
        db_healthy = False
        db_connection_count = 0
    
    # Redis health
    try:
        redis_client.ping()
        redis_healthy = True
        redis_info = redis_client.info()
        redis_memory = redis_info.get('used_memory_human', 'N/A')
        redis_connected_clients = redis_info.get('connected_clients', 0)
    except Exception as e:
        redis_healthy = False
        redis_memory = 'N/A'
        redis_connected_clients = 0
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used_gb": round(memory.used / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2)
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
                "used_gb": round(disk.used / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2)
            }
        },
        "services": {
            "database": {
                "healthy": db_healthy,
                "active_connections": db_connection_count
            },
            "redis": {
                "healthy": redis_healthy,
                "memory_used": redis_memory,
                "connected_clients": redis_connected_clients
            }
        }
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check for all services"""
    
    import time
    checks = {
        "database": {"healthy": False, "latency_ms": None},
        "redis": {"healthy": False, "latency_ms": None}
    }
    
    # Database check
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        checks["database"]["healthy"] = True
        checks["database"]["latency_ms"] = round((time.time() - start) * 1000, 2)
    except Exception as e:
        checks["database"]["error"] = str(e)
    
    # Redis check
    try:
        start = time.time()
        redis_client.ping()
        checks["redis"]["healthy"] = True
        checks["redis"]["latency_ms"] = round((time.time() - start) * 1000, 2)
    except Exception as e:
        checks["redis"]["error"] = str(e)
    
    all_healthy = all(check["healthy"] for check in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
