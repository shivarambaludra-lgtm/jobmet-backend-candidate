from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.core.database import get_db
from app.models.user import User
from app.models.user_activity import UserActivity
from app.models.job_application import JobApplication, ApplicationStatus
from app.models.bookmark import Bookmark
from app.models.saved_search import SavedSearch
from app.api.v1.auth import get_current_user
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's analytics dashboard"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 1. Application statistics
    total_applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).count()
    
    applications_by_status = db.query(
        JobApplication.status,
        func.count(JobApplication.id)
    ).filter(
        JobApplication.user_id == current_user.id
    ).group_by(JobApplication.status).all()
    
    # 2. Search activity
    total_searches = db.query(UserActivity).filter(
        UserActivity.user_id == current_user.id,
        UserActivity.activity_type == "search",
        UserActivity.created_at >= start_date
    ).count()
    
    # 3. Bookmarks
    total_bookmarks = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).count()
    
    # 4. Saved searches
    active_saved_searches = db.query(SavedSearch).filter(
        SavedSearch.user_id == current_user.id,
        SavedSearch.is_active == True
    ).count()
    
    # 5. Activity timeline (last N days)
    daily_activity = db.query(
        func.date(UserActivity.created_at).label('date'),
        func.count(UserActivity.id).label('count')
    ).filter(
        UserActivity.user_id == current_user.id,
        UserActivity.created_at >= start_date
    ).group_by(func.date(UserActivity.created_at)).all()
    
    # 6. Recent applications (last 7 days)
    recent_apps = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.applied_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    return {
        "summary": {
            "total_applications": total_applications,
            "total_bookmarks": total_bookmarks,
            "total_searches": total_searches,
            "active_saved_searches": active_saved_searches,
            "recent_applications_7d": recent_apps
        },
        "applications_by_status": {
            str(status.value): count
            for status, count in applications_by_status
        },
        "activity_timeline": [
            {"date": str(date), "count": count}
            for date, count in daily_activity
        ],
        "period_days": days
    }

@router.get("/conversion-funnel")
async def get_conversion_funnel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get application conversion funnel"""
    
    # Count activities at each stage
    total_views = db.query(UserActivity).filter(
        UserActivity.user_id == current_user.id,
        UserActivity.activity_type == 'view_job'
    ).count()
    
    total_bookmarks = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).count()
    
    total_applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).count()
    
    interviews = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.status.in_([
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.OFFER,
            ApplicationStatus.ACCEPTED
        ])
    ).count()
    
    offers = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        ApplicationStatus.status.in_([
            ApplicationStatus.OFFER,
            ApplicationStatus.ACCEPTED
        ])
    ).count()
    
    # Calculate conversion rates
    def calc_percentage(numerator, denominator):
        if denominator == 0:
            return 0
        return round((numerator / denominator) * 100, 1)
    
    return {
        "funnel": [
            {
                "stage": "Viewed",
                "count": total_views,
                "percentage": 100
            },
            {
                "stage": "Bookmarked",
                "count": total_bookmarks,
                "percentage": calc_percentage(total_bookmarks, total_views)
            },
            {
                "stage": "Applied",
                "count": total_applications,
                "percentage": calc_percentage(total_applications, total_views)
            },
            {
                "stage": "Interview",
                "count": interviews,
                "percentage": calc_percentage(interviews, total_applications)
            },
            {
                "stage": "Offer",
                "count": offers,
                "percentage": calc_percentage(offers, total_applications)
            }
        ],
        "conversion_rates": {
            "view_to_bookmark": calc_percentage(total_bookmarks, total_views),
            "view_to_apply": calc_percentage(total_applications, total_views),
            "apply_to_interview": calc_percentage(interviews, total_applications),
            "apply_to_offer": calc_percentage(offers, total_applications)
        }
    }

@router.get("/top-companies")
async def get_top_companies(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top companies by application count"""
    
    top_companies = db.query(
        JobApplication.job_posting_id,
        func.count(JobApplication.id).label('app_count')
    ).join(
        JobApplication.job_posting
    ).filter(
        JobApplication.user_id == current_user.id
    ).group_by(
        JobApplication.job_posting_id
    ).order_by(
        func.count(JobApplication.id).desc()
    ).limit(limit).all()
    
    # Get company details
    result = []
    for job_id, count in top_companies:
        from app.models.job_posting import JobPosting
        job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
        if job:
            result.append({
                "company": job.company,
                "application_count": count
            })
    
    return {
        "top_companies": result
    }

@router.get("/activity-heatmap")
async def get_activity_heatmap(
    days: int = Query(90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity heatmap data"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily activity counts
    daily_counts = db.query(
        func.date(UserActivity.created_at).label('date'),
        UserActivity.activity_type,
        func.count(UserActivity.id).label('count')
    ).filter(
        UserActivity.user_id == current_user.id,
        UserActivity.created_at >= start_date
    ).group_by(
        func.date(UserActivity.created_at),
        UserActivity.activity_type
    ).all()
    
    # Format for heatmap
    heatmap_data = {}
    for date, activity_type, count in daily_counts:
        date_str = str(date)
        if date_str not in heatmap_data:
            heatmap_data[date_str] = {}
        heatmap_data[date_str][activity_type] = count
    
    return {
        "heatmap": heatmap_data,
        "period_days": days
    }
