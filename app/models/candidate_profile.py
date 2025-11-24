from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base
import uuid
from datetime import datetime

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Professional info
    headline = Column(String(255))
    bio = Column(Text)
    years_experience = Column(Integer)
    
    # JSON columns for flexible data
    skills = Column(JSONB)  # [{"name": "Java", "level": "Expert", "years": 5}]
    education = Column(JSONB)  # [{"degree": "MS", "field": "CS", "university": "Stanford"}]
    experience = Column(JSONB)  # [{"title": "Senior Dev", "company": "Google", "years": 3}]
    certifications = Column(JSONB)
    
    # Location & visa
    location = Column(String(255))
    visa_status = Column(String(50))  # 'H1B', 'Green Card', 'Citizen', 'Needs Sponsorship'
    willing_to_relocate = Column(Boolean, default=False)
    preferred_locations = Column(JSONB)  # ["San Francisco", "Seattle"]
    
    # Social profiles
    github_url = Column(String(500))
    linkedin_url = Column(String(500))
    portfolio_url = Column(String(500))
    references = Column(JSONB)
    
    # Resume
    resume_text = Column(Text)
    resume_embedding = Column(Vector(1536))  # pgvector for semantic search
    
    # Metadata
    profile_complete = Column(Integer, default=0)  # 0-100%
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="profile")
