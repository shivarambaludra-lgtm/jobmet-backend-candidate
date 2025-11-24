from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class SavedSearch(Base):
    """User's saved search queries"""
    __tablename__ = "saved_searches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Search details
    name = Column(String, nullable=False)  # "Remote Python Jobs"
    query = Column(Text, nullable=False)
    parsed_query = Column(JSONB)
    
    # Notification settings
    email_alerts = Column(Boolean, default=False)
    alert_frequency = Column(String, default="daily")  # "daily", "weekly", "never"
    
    # Stats
    last_run_at = Column(DateTime)
    new_jobs_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    user = relationship("User", backref="saved_searches")
