from app.services.crawler.base_crawler import BaseCrawler, RawJobData
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
from fake_useragent import UserAgent
import re

class LinkedInCrawler(BaseCrawler):
    """Crawler for LinkedIn Jobs"""
    
    def __init__(self, rate_limit: int = 5):
        super().__init__(rate_limit)
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.ua = UserAgent()
        
    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 100
    ) -> List[RawJobData]:
        """Search LinkedIn jobs"""
        
        jobs = []
        start = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while len(jobs) < max_results:
                params = {
                    "keywords": query,
                    "location": location or "",
                    "start": start,
                    "f_TPR": "r86400"  # Last 24 hours
                }
                
                headers = {
                    "User-Agent": self.ua.random,
                    "Accept": "text/html,application/xhtml+xml",
                }
                
                try:
                    response = await client.get(
                        self.base_url,
                        params=params,
                        headers=headers,
                        follow_redirects=True
                    )
                    
                    if response.status_code != 200:
                        print(f"LinkedIn: Status {response.status_code}")
                        break
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='base-card')
                    
                    if not job_cards:
                        break
                    
                    for card in job_cards:
                        try:
                            title_elem = card.find('h3', class_='base-search-card__title')
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            location_elem = card.find('span', class_='job-search-card__location')
                            link_elem = card.find('a', class_='base-card__full-link')
                            
                            if not all([title_elem, company_elem, link_elem]):
                                continue
                            
                            job_url = link_elem.get('href', '').split('?')[0]
                            
                            jobs.append(RawJobData(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip(),
                                location=location_elem.text.strip() if location_elem else None,
                                description="",  # Will fetch later
                                url=job_url,
                                source="linkedin",
                                source_category="job_board",
                                external_id=self._extract_job_id(job_url)
                            ))
                            
                        except Exception as e:
                            print(f"Error parsing LinkedIn job card: {e}")
                            continue
                    
                    start += 25
                    await self.rate_limit_delay()
                    
                except Exception as e:
                    print(f"Error fetching LinkedIn jobs: {e}")
                    break
        
        return jobs[:max_results]
    
    async def get_job_details(self, job_url: str) -> Optional[RawJobData]:
        """Get detailed job description from LinkedIn"""
        
        headers = {"User-Agent": self.ua.random}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(job_url, headers=headers)
                
                if response.status_code != 200:
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                description_elem = soup.find('div', class_='show-more-less-html__markup')
                description = description_elem.get_text(strip=True) if description_elem else ""
                
                return RawJobData(
                    title="",
                    company="",
                    description=description,
                    url=job_url,
                    source="linkedin",
                    source_category="job_board",
                    raw_html=response.text
                )
                
            except Exception as e:
                print(f"Error fetching LinkedIn job details: {e}")
                return None
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        """Extract job ID from LinkedIn URL"""
        match = re.search(r'/jobs/view/(\d+)', url)
        return match.group(1) if match else None
