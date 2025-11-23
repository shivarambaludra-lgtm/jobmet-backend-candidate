from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.workflows.apply_graph import build_apply_graph
from app.models.application import Application
from pydantic import BaseModel
from typing import List
from app.services.recommendation_service import JobRecommendationService

router = APIRouter()

class ApplyRequest(BaseModel):
    candidate_id: int
    job_id: int
    resume: str

class BulkApplyRequest(BaseModel):
    candidate_id: int
    job_ids: List[int]
    resume: str

@router.post("/apply")
async def apply_job(request: ApplyRequest):
    graph = build_apply_graph()
    result = graph.invoke({
        "candidate_id": request.candidate_id,
        "job_id": request.job_id,
        "resume": request.resume
    })
    return result

@router.post("/apply/bulk")
async def bulk_apply(
    request: BulkApplyRequest,
    db: Session = Depends(get_db)
):
    """Apply to multiple jobs at once"""
    results = []
    
    for job_id in request.job_ids:
        try:
            graph = build_apply_graph()
            result = graph.invoke({
                "candidate_id": request.candidate_id,
                "job_id": job_id,
                "resume": request.resume
            })
            
            results.append({
                "job_id": job_id,
                "success": True,
                "application_id": result.get("application_id"),
                "score": result.get("score"),
                "status": result.get("status"),
                "message": result.get("message", "")[:100]  # Truncate long messages
            })
        except Exception as e:
            results.append({
                "job_id": job_id,
                "success": False,
                "error": str(e)
            })
    
    successful = sum(1 for r in results if r["success"])
    
    return {
        "candidate_id": request.candidate_id,
        "total_jobs": len(request.job_ids),
        "successful": successful,
        "failed": len(request.job_ids) - successful,
        "results": results,
        "summary": {
            "accepted": sum(1 for r in results if r.get("status") == "accept"),
            "under_review": sum(1 for r in results if r.get("status") == "review"),
            "rejected": sum(1 for r in results if r.get("status") == "reject")
        }
    }

@router.get("/applications/{application_id}")
async def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get single application by ID"""
    app = db.query(Application).filter(
        Application.id == application_id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return app.to_dict()


@router.get("/candidate/{candidate_id}/applications")
async def list_candidate_applications(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """List all applications for a candidate"""
    apps = db.query(Application).filter(
        Application.candidate_id == candidate_id
    ).order_by(Application.applied_at.desc()).all()
    
    return {
        "candidate_id": candidate_id,
        "total": len(apps),
        "applications": [app.to_dict() for app in apps]
    }


@router.get("/candidate/{candidate_id}/stats")
async def get_candidate_stats(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Get candidate application statistics"""
    apps = db.query(Application).filter(
        Application.candidate_id == candidate_id
    ).all()
    
    if not apps:
        return {
            "candidate_id": candidate_id,
            "total_applications": 0,
            "average_score": 0,
            "status_breakdown": {}
        }
    
    scores = [a.match_score for a in apps if a.match_score]
    
    return {
        "candidate_id": candidate_id,
        "total_applications": len(apps),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "highest_score": max(scores) if scores else 0,
        "lowest_score": min(scores) if scores else 0,
        "status_breakdown": {
            "accept": sum(1 for a in apps if a.status == "accept"),
            "review": sum(1 for a in apps if a.status == "review"),
            "reject": sum(1 for a in apps if a.status == "reject")
        },
        "top_strengths": _get_top_strengths(apps)
    }

@router.post("/candidate/recommend-jobs")
async def recommend_jobs(
    request: dict,  # {"resume": "..."}
    top_n: int = 10,
    min_score: int = 50
):
    """
    Get job recommendations for a candidate
    
    - **resume**: Candidate's resume text
    - **top_n**: Number of recommendations (default: 10)
    - **min_score**: Minimum match score to include (default: 50)
    """
    if "resume" not in request or not request["resume"]:
        raise HTTPException(400, "Resume text is required")
    
    service = JobRecommendationService()
    recommendations = service.recommend_jobs(
        resume_text=request["resume"],
        top_n=top_n,
        min_score=min_score
    )
    
    return {
        "total_recommendations": len(recommendations),
        "min_score_threshold": min_score,
        "recommendations": recommendations
    }

def _get_top_strengths(apps):
    """Extract most common strengths from applications"""
    from collections import Counter
    all_strengths = []
    for app in apps:
        if app.strengths:
            all_strengths.extend(app.strengths)
    
    if not all_strengths:
        return []
    
    counter = Counter(all_strengths)
    return [{"strength": s, "count": c} for s, c in counter.most_common(5)]
