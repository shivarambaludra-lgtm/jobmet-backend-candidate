from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job import Job
from app.models.candidate import Candidate
from app.services.recommendation_service import JobRecommendationService
from pydantic import BaseModel

router = APIRouter()

class RecommendationRequest(BaseModel):
    resume: str

@router.get("/recommendations/{candidate_id}")
async def get_job_recommendations(candidate_id: int, db: Session = Depends(get_db)):
    """Get recommended jobs for a candidate based on their resume (from DB)"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found")
    
    if not candidate.resume_text:
         return {"message": "Candidate has no resume text", "recommendations": []}
    
    service = JobRecommendationService()
    recommendations = service.recommend_jobs(
        resume_text=candidate.resume_text,
        top_n=10
    )
    
    return {
        "candidate_id": candidate_id,
        "candidate_name": f"{candidate.first_name} {candidate.last_name}",
        "recommendations": recommendations
    }

@router.post("/recommend-jobs")
async def recommend_jobs_manual(
    request: RecommendationRequest,
    top_n: int = 10,
    min_score: int = 50
):
    """
    Get job recommendations for a raw resume text
    """
    service = JobRecommendationService()
    recommendations = service.recommend_jobs(
        resume_text=request.resume,
        top_n=top_n,
        min_score=min_score
    )
    
    return {
        "total_recommendations": len(recommendations),
        "min_score_threshold": min_score,
        "recommendations": recommendations
    }
