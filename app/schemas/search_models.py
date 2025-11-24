from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class JobResult(BaseModel):
    """Individual job search result"""
    id: str
    title: str
    company: str
    location: str
    description: str
    skills: List[str]
    experience_required: int
    salary_range: Optional[str] = None
    visa_sponsorship: bool
    source: str  # "job_board", "career_page", "hiring_post"
    url: str
    posted_date: datetime
    match_score: float

class SearchResponse(BaseModel):
    """Complete search response with categorized results"""
    query: str
    parsed_query: Dict
    total_results: int
    job_boards: List[JobResult]
    career_pages: List[JobResult]
    hiring_posts: List[JobResult]
    processing_time: float
    filters: Optional[Dict[str, Any]] = None  # Dynamic filters
