from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ParsedQuery(BaseModel):
    """Structured representation of a parsed job search query"""
    job_title: str = Field(..., description="Primary job role")
    skills_required: List[str] = Field(default_factory=list, description="Technical skills extracted")
    years_experience: Optional[int] = Field(None, description="Years of experience required")
    location: Optional[str] = Field(None, description="Preferred location")
    remote: bool = Field(default=False, description="Remote work allowed")
    visa_requirements: Optional[str] = Field(None, description="Visa sponsorship needs")
    education_level: Optional[str] = Field(None, description="Minimum education")
    salary_min: Optional[int] = Field(None, description="Minimum salary")
    salary_max: Optional[int] = Field(None, description="Maximum salary")
    company_size: Optional[str] = Field(None, description="Startup, mid-size, enterprise")
    industry: Optional[str] = Field(None, description="Target industry")

class EnrichedQuery(BaseModel):
    """Query enriched with knowledge graph data"""
    original_query: ParsedQuery
    expanded_job_titles: List[str] = Field(default_factory=list, description="Synonym job titles")
    related_skills: List[str] = Field(default_factory=list, description="Related technical skills")
    sponsor_companies: List[Dict[str, str]] = Field(default_factory=list, description="Companies offering sponsorship")
    education_alternatives: List[str] = Field(default_factory=list, description="Alternative education levels")

class SearchRequest(BaseModel):
    """Request model for job search"""
    query: str = Field(..., min_length=3, description="Natural language search query")
    candidate_id: Optional[str] = Field(None, description="Optional candidate ID for personalization")
