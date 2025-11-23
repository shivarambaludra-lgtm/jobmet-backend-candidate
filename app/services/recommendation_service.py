"""
Job recommendation service
Finds best matching jobs for a candidate's resume
"""
from typing import List, Tuple
from app.services.llm_service import ResumeMatchingService
from app.models.job import Job
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class JobRecommendationService:
    """Find best jobs for a candidate"""
    
    def __init__(self):
        self.matcher = ResumeMatchingService()
    
    def recommend_jobs(
        self,
        resume_text: str,
        top_n: int = 10,
        min_score: int = 50
    ) -> List[dict]:
        """
        Score candidate against all jobs and return top matches
        
        Args:
            resume_text: Candidate's resume
            top_n: Number of recommendations to return
            min_score: Minimum match score to include
            
        Returns:
            List of job recommendations with scores
        """
        db = SessionLocal()
        
        try:
            # Get all jobs
            jobs = db.query(Job).all()
            logger.info(f"Scoring candidate against {len(jobs)} jobs")
            
            # Score each job
            scored_jobs = []
            for job in jobs:
                try:
                    result = self.matcher.score_candidate(
                        resume_text=resume_text,
                        job_description=f"{job.title}\n\n{job.description}",
                        requirements=job.requirements
                    )
                    
                    if result.match_score >= min_score:
                        scored_jobs.append({
                            "job_id": job.id,
                            "title": job.title,
                            "description": job.description[:200] + "...",
                            "match_score": result.match_score,
                            "recommendation": result.recommendation,
                            "strengths": result.strengths,
                            "gaps": result.gaps,
                            "reasoning": result.reasoning[:150] + "..."
                        })
                except Exception as e:
                    logger.error(f"Error scoring job {job.id}: {str(e)}")
                    continue
            
            # Sort by score descending
            scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
            
            return scored_jobs[:top_n]
            
        finally:
            db.close()
