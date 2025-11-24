from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.job_posting import JobPosting
from app.models.user_activity import UserActivity
from app.api.v1.auth import get_current_user
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

class BookmarkCreate(BaseModel):
    job_posting_id: UUID
    notes: Optional[str] = ""

class BookmarkResponse(BaseModel):
    id: str
    job: dict
    notes: Optional[str]
    created_at: datetime

@router.post("/", status_code=201)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bookmark a job for later review"""
    
    # Check if job exists
    job = db.query(JobPosting).filter(JobPosting.id == bookmark_data.job_posting_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already bookmarked
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.job_posting_id == bookmark_data.job_posting_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Job already bookmarked")
    
    # Create bookmark
    bookmark = Bookmark(
        user_id=current_user.id,
        job_posting_id=bookmark_data.job_posting_id,
        notes=bookmark_data.notes
    )
    db.add(bookmark)
    
    # Track activity
    activity = UserActivity(
        user_id=current_user.id,
        activity_type="bookmark",
        job_posting_id=bookmark_data.job_posting_id,
        activity_data={
            "job_title": job.title,
            "company": job.company
        }
    )
    db.add(activity)
    
    db.commit()
    db.refresh(bookmark)
    
    return {
        "id": str(bookmark.id),
        "message": "Job bookmarked successfully"
    }

@router.get("/", response_model=List[BookmarkResponse])
async def get_bookmarks(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's bookmarked jobs"""
    
    bookmarks = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).order_by(Bookmark.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for b in bookmarks:
        result.append(BookmarkResponse(
            id=str(b.id),
            job={
                "id": str(b.job_posting.id),
                "title": b.job_posting.title,
                "company": b.job_posting.company,
                "location": b.job_posting.location,
                "url": b.job_posting.url,
                "visa_sponsorship": b.job_posting.visa_sponsorship,
                "salary_min": b.job_posting.salary_min,
                "salary_max": b.job_posting.salary_max
            },
            notes=b.notes,
            created_at=b.created_at
        ))
    
    return result

@router.get("/{bookmark_id}")
async def get_bookmark(
    bookmark_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific bookmark"""
    
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    return {
        "id": str(bookmark.id),
        "job": {
            "id": str(bookmark.job_posting.id),
            "title": bookmark.job_posting.title,
            "company": bookmark.job_posting.company,
            "location": bookmark.job_posting.location,
            "description": bookmark.job_posting.description,
            "skills": bookmark.job_posting.skills,
            "url": bookmark.job_posting.url,
            "visa_sponsorship": bookmark.job_posting.visa_sponsorship,
            "salary_min": bookmark.job_posting.salary_min,
            "salary_max": bookmark.job_posting.salary_max,
            "posted_date": bookmark.job_posting.posted_date
        },
        "notes": bookmark.notes,
        "created_at": bookmark.created_at
    }

@router.patch("/{bookmark_id}")
async def update_bookmark(
    bookmark_id: UUID,
    notes: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update bookmark notes"""
    
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    bookmark.notes = notes
    db.commit()
    
    return {"message": "Bookmark updated successfully"}

@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a bookmark"""
    
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(bookmark)
    db.commit()
    
    return {"message": "Bookmark removed successfully"}

@router.get("/stats/summary")
async def get_bookmark_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get bookmark statistics"""
    
    total = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).count()
    
    return {
        "total_bookmarks": total
    }
