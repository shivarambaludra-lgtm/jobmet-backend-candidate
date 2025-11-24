from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])

# ============= Request Models =============

class SkillItem(BaseModel):
    name: str
    level: str  # "Beginner", "Intermediate", "Expert"
    years: int

class ProfileUpdateRequest(BaseModel):
    headline: Optional[str] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    skills: Optional[List[SkillItem]] = None
    location: Optional[str] = None
    visa_status: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

# ============= Endpoints =============

@router.get("/")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidate profile"""
    
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": str(profile.id),
        "headline": profile.headline,
        "bio": profile.bio,
        "years_experience": profile.years_experience,
        "skills": profile.skills,
        "location": profile.location,
        "visa_status": profile.visa_status,
        "profile_complete": profile.profile_complete
    }

@router.put("/")
async def update_profile(
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update candidate profile"""
    
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return {"message": "Profile updated successfully"}
