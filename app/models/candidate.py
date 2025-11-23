"""
Candidate model with relationship to applications
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Candidate(Base):
    """Candidate profile with resume"""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    resume_text = Column(Text, nullable=True)
    
    # Relationship to applications
    applications = relationship("Application", back_populates="candidate")
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name={self.first_name} {self.last_name})>"
