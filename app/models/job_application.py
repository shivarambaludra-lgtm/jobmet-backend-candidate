from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime
import enum

class ApplicationStatus(str, enum.Enum):
    """Application status enum"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ACCEPTED = "accepted"

class JobApplication(Base):
    """Enhanced job application tracking"""
    __tablename__ = "job_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False, index=True)
    
    # Application details
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, index=True)
    cover_letter = Column(Text)
    resume_used = Column(String)  # Link to resume file/version
    
    # Timeline
    applied_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tracking
    application_url = Column(String)  # External application URL
    confirmation_email = Column(String)  # Confirmation email received
    interview_dates = Column(JSONB)  # [{"date": "...", "type": "phone", "notes": "..."}]
    notes = Column(Text)  # User's notes
    
    # Relationships
    user = relationship("User", backref="applications")
    job_posting = relationship("JobPosting", backref="applications")
