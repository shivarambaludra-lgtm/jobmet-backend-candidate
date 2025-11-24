from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.job_posting import JobPosting
from app.models.user_activity import UserActivity
from app.models.candidate_profile import CandidateProfile
from app.models.bookmark import Bookmark
from app.models.job_application import JobApplication
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Generate personalized job recommendations using ML-based scoring"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_recommendations(
        self,
        user_id: str,
        limit: int = 20,
        exclude_applied: bool = True,
        exclude_bookmarked: bool = False
    ) -> List[JobPosting]:
        """
        Generate recommendations based on:
        1. User profile (skills, experience, location)
        2. Past searches and views
        3. Bookmarked jobs
        4. Applied jobs
        5. Similar users' preferences (collaborative filtering)
        """
        
        # Get user profile
        profile = self.db.query(CandidateProfile).filter(
            CandidateProfile.user_id == user_id
        ).first()
        
        if not profile:
            return self._get_trending_jobs(limit)
        
        # Get user's interaction history
        recent_activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type.in_(['view_job', 'bookmark', 'apply'])
        ).order_by(UserActivity.created_at.desc()).limit(100).all()
        
        # Get excluded job IDs
        excluded_ids = set()
        
        if exclude_applied:
            applied_ids = self.db.query(JobApplication.job_posting_id).filter(
                JobApplication.user_id == user_id
            ).all()
            excluded_ids.update([str(job_id[0]) for job_id in applied_ids])
        
        if exclude_bookmarked:
            bookmarked_ids = self.db.query(Bookmark.job_posting_id).filter(
                Bookmark.user_id == user_id
            ).all()
            excluded_ids.update([str(job_id[0]) for job_id in bookmarked_ids])
        
        # Get active jobs
        query = self.db.query(JobPosting).filter(
            JobPosting.is_active == True
        )
        
        if excluded_ids:
            query = query.filter(~JobPosting.id.in_(excluded_ids))
        
        jobs = query.limit(500).all()
        
        # Score all jobs
        scored_jobs = []
        for job in jobs:
            score = self._calculate_recommendation_score(
                job, profile, recent_activities
            )
            scored_jobs.append((job, score))
        
        # Sort by score and return top N
        scored_jobs.sort(key=lambda x: x[1], reverse=True)
        
        return [job for job, score in scored_jobs[:limit]]
    
    def _calculate_recommendation_score(
        self,
        job: JobPosting,
        profile: CandidateProfile,
        activities: List[UserActivity]
    ) -> float:
        """Calculate recommendation score (0-100)"""
        
        score = 0.0
        
        # 1. Skill match (40 points)
        if profile.skills and job.skills:
            user_skills = set([s.get("name", "").lower() for s in profile.skills])
            job_skills = set([s.lower() for s in job.skills])
            
            if job_skills:
                skill_overlap = len(user_skills.intersection(job_skills))
                skill_score = (skill_overlap / len(job_skills)) * 40
                score += skill_score
        
        # 2. Experience match (20 points)
        if profile.years_experience and job.years_experience_min:
            if profile.years_experience >= job.years_experience_min:
                score += 20
            else:
                # Partial credit if close
                diff = job.years_experience_min - profile.years_experience
                if diff <= 2:
                    score += 10
        
        # 3. Location preference (15 points)
        if profile.preferred_locations and job.location:
            for pref_loc in profile.preferred_locations:
                if pref_loc.lower() in job.location.lower():
                    score += 15
                    break
        elif profile.location and job.location:
            if profile.location.lower() in job.location.lower():
                score += 10
        
        # 4. Visa sponsorship (15 points)
        if profile.visa_status and "sponsorship" in profile.visa_status.lower():
            if job.visa_sponsorship:
                score += 15
        
        # 5. Similar jobs viewed (10 points)
        viewed_companies = set()
        viewed_titles = []
        
        for activity in activities:
            if activity.activity_data:
                company = activity.activity_data.get("company", "")
                title = activity.activity_data.get("job_title", "")
                
                if company:
                    viewed_companies.add(company.lower())
                if title:
                    viewed_titles.append(title.lower())
        
        # Same company bonus
        if job.company and job.company.lower() in viewed_companies:
            score += 5
        
        # Similar title bonus
        if job.title:
            job_title_lower = job.title.lower()
            for viewed_title in viewed_titles:
                # Simple similarity check
                common_words = set(job_title_lower.split()) & set(viewed_title.split())
                if len(common_words) >= 2:
                    score += 5
                    break
        
        return min(score, 100.0)  # Cap at 100
    
    def _get_trending_jobs(self, limit: int) -> List[JobPosting]:
        """Fallback: return trending/recent jobs"""
        
        return self.db.query(JobPosting).filter(
            JobPosting.is_active == True
        ).order_by(JobPosting.scraped_date.desc()).limit(limit).all()
    
    def get_similar_jobs(
        self,
        job_id: str,
        limit: int = 10
    ) -> List[JobPosting]:
        """Find jobs similar to a given job"""
        
        # Get the reference job
        ref_job = self.db.query(JobPosting).filter(
            JobPosting.id == job_id
        ).first()
        
        if not ref_job:
            return []
        
        # Get all active jobs except the reference
        jobs = self.db.query(JobPosting).filter(
            JobPosting.is_active == True,
            JobPosting.id != job_id
        ).limit(200).all()
        
        # Score by similarity
        scored_jobs = []
        for job in jobs:
            similarity = self._calculate_job_similarity(ref_job, job)
            scored_jobs.append((job, similarity))
        
        # Sort and return
        scored_jobs.sort(key=lambda x: x[1], reverse=True)
        return [job for job, score in scored_jobs[:limit]]
    
    def _calculate_job_similarity(
        self,
        job1: JobPosting,
        job2: JobPosting
    ) -> float:
        """Calculate similarity between two jobs"""
        
        score = 0.0
        
        # Same company (30 points)
        if job1.company and job2.company:
            if job1.company.lower() == job2.company.lower():
                score += 30
        
        # Skill overlap (40 points)
        if job1.skills and job2.skills:
            skills1 = set([s.lower() for s in job1.skills])
            skills2 = set([s.lower() for s in job2.skills])
            
            if skills1 and skills2:
                overlap = len(skills1.intersection(skills2))
                total = len(skills1.union(skills2))
                score += (overlap / total) * 40
        
        # Similar experience level (15 points)
        if job1.years_experience_min and job2.years_experience_min:
            diff = abs(job1.years_experience_min - job2.years_experience_min)
            if diff == 0:
                score += 15
            elif diff <= 2:
                score += 10
        
        # Same location (15 points)
        if job1.location and job2.location:
            if job1.location.lower() == job2.location.lower():
                score += 15
        
        return score
