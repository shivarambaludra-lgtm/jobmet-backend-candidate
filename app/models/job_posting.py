from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import uuid
from datetime import datetime

class JobPosting(Base):
    """Crawled job posting from various sources"""
    __tablename__ = "job_postings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job Details
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    location = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    
    # Structured Data
    skills = Column(JSONB)
    years_experience_min = Column(Integer)
    years_experience_max = Column(Integer)
    education_required = Column(String)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String, default="USD")
    
    # Visa & Work Authorization
    visa_sponsorship = Column(Boolean, default=False)
    requires_citizenship = Column(Boolean, default=False)
    work_authorization = Column(JSONB)
    
    # Source Information
    source = Column(String, nullable=False, index=True)
    source_category = Column(String, index=True)
    url = Column(String, unique=True, nullable=False)
    external_id = Column(String)
    
    # Metadata
    posted_date = Column(DateTime)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    raw_html = Column(Text)
    
    # Embeddings (for future semantic search)
    description_embedding = Column(ARRAY(Float))
    
    # Match score (set dynamically, not persisted)
    match_score = None

class SearchResult(Base):
    """Cached search results"""
    __tablename__ = "search_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    query_hash = Column(String, unique=True, index=True)
    original_query = Column(Text)
    parsed_query = Column(JSONB)
    enriched_query = Column(JSONB)
    
    job_posting_ids = Column(JSONB)
    total_results = Column(Integer)
    
    job_board_ids = Column(JSONB)
    career_page_ids = Column(JSONB)
    hiring_post_ids = Column(JSONB)
    
    candidate_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    processing_time = Column(Float)
