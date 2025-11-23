"""
Application model - tracks candidate job applications
"""
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String, default="pending")
    match_score = Column(Float, nullable=True)
    strengths = Column(JSON, default=[])
    gaps = Column(JSON, default=[])
    ai_reasoning = Column(String, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")

    def to_dict(self):
        """Convert application to dictionary"""
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "status": self.status,
            "match_score": self.match_score,
            "strengths": self.strengths,
            "gaps": self.gaps,
            "ai_reasoning": self.ai_reasoning,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None
        }
