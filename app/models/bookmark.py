from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class Bookmark(Base):
    """User's bookmarked jobs"""
    __tablename__ = "bookmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    job_posting_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)  # User's private notes
    
    # Relationships
    user = relationship("User", backref="bookmarks")
    job_posting = relationship("JobPosting", backref="bookmarked_by")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'job_posting_id', name='unique_user_job_bookmark'),
    )
