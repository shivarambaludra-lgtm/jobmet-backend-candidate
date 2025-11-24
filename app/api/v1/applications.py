from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.user import User
from app.models.job_application import JobApplication, ApplicationStatus
from app.models.job_posting import JobPosting
from app.models.user_activity import UserActivity
from app.api.v1.auth import get_current_user
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/applications", tags=["applications"])

class ApplicationCreate(BaseModel):
    job_posting_id: UUID
    cover_letter: Optional[str] = None
    resume_used: Optional[str] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    interview_date: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    job: dict
    status: str
    applied_at: datetime
    last_updated: datetime
    notes: Optional[str]
    interview_dates: Optional[list]

@router.post("/", status_code=201)
async def create_application(
    application_data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track a job application"""
    
    # Check if job exists
    job = db.query(JobPosting).filter(
        JobPosting.id == application_data.job_posting_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already applied
    existing = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_posting_id == application_data.job_posting_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")
    
    # Create application
    application = JobApplication(
        user_id=current_user.id,
        job_posting_id=application_data.job_posting_id,
        cover_letter=application_data.cover_letter,
        resume_used=application_data.resume_used,
        notes=application_data.notes,
        status=ApplicationStatus.SUBMITTED
    )
    db.add(application)
    
    # Track activity
    activity = UserActivity(
        user_id=current_user.id,
        activity_type="apply",
        job_posting_id=application_data.job_posting_id,
        activity_data={
            "job_title": job.title,
            "company": job.company
        }
    )
    db.add(activity)
    
    db.commit()
    db.refresh(application)
    
    return {
        "id": str(application.id),
        "message": "Application tracked successfully"
    }

@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(
    status: Optional[ApplicationStatus] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's job applications"""
    
    query = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    )
    
    if status:
        query = query.filter(JobApplication.status == status)
    
    applications = query.order_by(
        JobApplication.applied_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for app in applications:
        result.append(ApplicationResponse(
            id=str(app.id),
            job={
                "id": str(app.job_posting.id),
                "title": app.job_posting.title,
                "company": app.job_posting.company,
                "location": app.job_posting.location,
                "url": app.job_posting.url
            },
            status=app.status.value,
            applied_at=app.applied_at,
            last_updated=app.last_updated,
            notes=app.notes,
            interview_dates=app.interview_dates
        ))
    
    return result

@router.get("/{application_id}")
async def get_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific application"""
    
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {
        "id": str(application.id),
        "job": {
            "id": str(application.job_posting.id),
            "title": application.job_posting.title,
            "company": application.job_posting.company,
            "location": application.job_posting.location,
            "description": application.job_posting.description,
            "url": application.job_posting.url,
            "salary_min": application.job_posting.salary_min,
            "salary_max": application.job_posting.salary_max
        },
        "status": application.status.value,
        "cover_letter": application.cover_letter,
        "resume_used": application.resume_used,
        "applied_at": application.applied_at,
        "last_updated": application.last_updated,
        "application_url": application.application_url,
        "confirmation_email": application.confirmation_email,
        "interview_dates": application.interview_dates,
        "notes": application.notes
    }

@router.patch("/{application_id}")
async def update_application(
    application_id: UUID,
    update_data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update application status"""
    
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Update status
    if update_data.status:
        application.status = update_data.status
    
    if update_data.notes:
        application.notes = update_data.notes
    
    if update_data.interview_date:
        # Add to interview dates array
        if not application.interview_dates:
            application.interview_dates = []
        application.interview_dates.append({
            "date": update_data.interview_date,
            "added_at": datetime.utcnow().isoformat()
        })
    
    db.commit()
    
    return {"message": "Application updated successfully"}

@router.post("/batch")
async def batch_apply(
    job_ids: List[UUID],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply to multiple jobs at once"""
    
    created = []
    skipped = []
    errors = []
    
    for job_id in job_ids:
        try:
            # Check if job exists
            job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
            if not job:
                errors.append({"job_id": str(job_id), "error": "Job not found"})
                continue
            
            # Check if already applied
            existing = db.query(JobApplication).filter(
                JobApplication.user_id == current_user.id,
                JobApplication.job_posting_id == job_id
            ).first()
            
            if existing:
                skipped.append(str(job_id))
                continue
            
            # Create application
            application = JobApplication(
                user_id=current_user.id,
                job_posting_id=job_id,
                status=ApplicationStatus.SUBMITTED
            )
            db.add(application)
            created.append(str(job_id))
            
        except Exception as e:
            errors.append({"job_id": str(job_id), "error": str(e)})
    
    db.commit()
    
    return {
        "created": len(created),
        "skipped": len(skipped),
        "errors": len(errors),
        "details": {
            "created_ids": created,
            "skipped_ids": skipped,
            "errors": errors
        },
        "message": f"Applied to {len(created)} jobs successfully"
    }

@router.get("/stats/summary")
async def get_application_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get application statistics"""
    
    total = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).count()
    
    by_status = db.query(
        JobApplication.status,
        func.count(JobApplication.id)
    ).filter(
        JobApplication.user_id == current_user.id
    ).group_by(JobApplication.status).all()
    
    return {
        "total_applications": total,
        "by_status": {
            status.value: count for status, count in by_status
        }
    }
