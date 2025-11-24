from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pydantic import BaseModel
import asyncio
from datetime import datetime

class RawJobData(BaseModel):
    """Raw job data from crawler before processing"""
    title: str
    company: str
    location: Optional[str] = None
    description: str
    url: str
    source: str  # "linkedin", "indeed", "glassdoor"
    source_category: str  # "job_board", "career_page", "hiring_post"
    external_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    raw_html: Optional[str] = None

class BaseCrawler(ABC):
    """Base class for all job crawlers"""
    
    def __init__(self, rate_limit: int = 10):
        """
        Args:
            rate_limit: Max requests per second
        """
        self.rate_limit = rate_limit
        self.source_name = self.__class__.__name__.replace("Crawler", "").lower()
    
    @abstractmethod
    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 100
    ) -> List[RawJobData]:
        """
        Search for jobs matching query
        
        Args:
            query: Job title/keywords
            location: Location filter
            max_results: Max jobs to return
            
        Returns:
            List of raw job data
        """
        pass
    
    @abstractmethod
    async def get_job_details(self, job_url: str) -> Optional[RawJobData]:
        """
        Get detailed job information from URL
        
        Args:
            job_url: Job posting URL
            
        Returns:
            Raw job data or None if failed
        """
        pass
    
    async def rate_limit_delay(self):
        """Implement rate limiting"""
        await asyncio.sleep(1.0 / self.rate_limit)
