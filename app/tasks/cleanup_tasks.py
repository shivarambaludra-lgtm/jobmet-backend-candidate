from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.search_result import SearchResult
from app.models.user_activity import UserActivity
from app.models.job_posting import JobPosting
from datetime import datetime, timedelta
from typing import Dict, Any

@celery_app.task(name="app.tasks.cleanup_tasks.cleanup_old_searches")
def cleanup_old_searches() -> Dict[str, Any]:
    """Delete expired search results from cache"""
    
    db = SessionLocal()
    
    try:
        expired_threshold = datetime.utcnow() - timedelta(days=7)
        
        deleted = db.query(SearchResult).filter(
            SearchResult.expires_at < expired_threshold
        ).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "deleted": deleted,
            "threshold": expired_threshold.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.cleanup_tasks.cleanup_old_activities")
def cleanup_old_activities() -> Dict[str, Any]:
    """Delete old user activities (keep last 90 days)"""
    
    db = SessionLocal()
    
    try:
        threshold = datetime.utcnow() - timedelta(days=90)
        
        deleted = db.query(UserActivity).filter(
            UserActivity.created_at < threshold
        ).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "deleted": deleted,
            "threshold": threshold.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.cleanup_tasks.cleanup_inactive_jobs")
def cleanup_inactive_jobs() -> Dict[str, Any]:
    """Mark old jobs as inactive (30+ days old)"""
    
    db = SessionLocal()
    
    try:
        threshold = datetime.utcnow() - timedelta(days=30)
        
        updated = db.query(JobPosting).filter(
            JobPosting.scraped_date < threshold,
            JobPosting.is_active == True
        ).update({"is_active": False})
        
        db.commit()
        
        return {
            "status": "success",
            "updated": updated,
            "threshold": threshold.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
