from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class UserActivity(Base):
    """Track user interactions for analytics"""
    __tablename__ = "user_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String, nullable=False, index=True)  # "search", "view_job", "apply", "bookmark"
    activity_data = Column(JSONB)  # Additional context
    
    # Job context (if applicable)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), index=True)
    
    # Session tracking
    session_id = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", backref="activities")
    job_posting = relationship("JobPosting", backref="user_activities")
