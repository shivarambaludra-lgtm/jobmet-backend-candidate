from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.recommendation_engine import RecommendationEngine
from typing import List
from uuid import UUID

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/")
async def get_recommendations(
    limit: int = Query(20, ge=1, le=100),
    exclude_applied: bool = True,
    exclude_bookmarked: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized job recommendations"""
    
    engine = RecommendationEngine(db)
    recommended_jobs = engine.get_recommendations(
        user_id=str(current_user.id),
        limit=limit,
        exclude_applied=exclude_applied,
        exclude_bookmarked=exclude_bookmarked
    )
    
    return {
        "total": len(recommended_jobs),
        "recommendations": [
            {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "skills": job.skills,
                "years_experience_min": job.years_experience_min,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "visa_sponsorship": job.visa_sponsorship,
                "url": job.url,
                "posted_date": job.posted_date
            }
            for job in recommended_jobs
        ]
    }

@router.get("/similar/{job_id}")
async def get_similar_jobs(
    job_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jobs similar to a specific job"""
    
    engine = RecommendationEngine(db)
    similar_jobs = engine.get_similar_jobs(
        job_id=str(job_id),
        limit=limit
    )
    
    return {
        "total": len(similar_jobs),
        "similar_jobs": [
            {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "skills": job.skills,
                "url": job.url
            }
            for job in similar_jobs
        ]
    }
