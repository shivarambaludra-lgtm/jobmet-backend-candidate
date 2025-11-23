from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.application import Application
from app.models.candidate import Candidate
from app.workflows.apply_graph import build_apply_graph
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ApplyRequest(BaseModel):
    candidate_id: int
    job_id: int
    resume: str

class BulkApplyRequest(BaseModel):
    """Request to apply to multiple jobs"""
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
                "message": result.get("message", "")[:100]
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

@router.get("/{candidate_id}/applications")
async def get_candidate_applications(candidate_id: int, db: Session = Depends(get_db)):
    """Get all applications for a candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found")
    
    applications = db.query(Application).filter(
        Application.candidate_id == candidate_id
    ).order_by(Application.applied_at.desc()).all()
    
    return {
        "candidate": {
            "id": candidate.id,
            "name": f"{candidate.first_name} {candidate.last_name}",
            "email": candidate.email
        },
        "applications": [
            {
                "id": app.id,
                "job_id": app.job_id,
                "job_title": app.job.title if app.job else "Unknown",
                "status": app.status,
                "score": app.match_score,
                "applied_at": app.applied_at
            }
            for app in applications
        ],
        "total": len(applications),
        "success_rate": sum(1 for a in applications if a.status == "accept") / len(applications) if applications else 0
    }

@router.get("/{candidate_id}/stats")
async def get_candidate_stats(candidate_id: int, db: Session = Depends(get_db)):
    """Get candidate statistics"""
    applications = db.query(Application).filter(
        Application.candidate_id == candidate_id
    ).all()
    
    if not applications:
        return {"total": 0, "success_rate": 0, "average_score": 0}
    
    scores = [a.match_score for a in applications if a.match_score]
    
    return {
        "total_applications": len(applications),
        "accepted": sum(1 for a in applications if a.status == "accept"),
        "under_review": sum(1 for a in applications if a.status == "review"),
        "rejected": sum(1 for a in applications if a.status == "reject"),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "success_rate": round(sum(1 for a in applications if a.status == "accept") / len(applications), 2)
    }
