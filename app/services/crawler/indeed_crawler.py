from app.services.crawler.base_crawler import BaseCrawler, RawJobData
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re

class IndeedCrawler(BaseCrawler):
    """Crawler for Indeed jobs"""
    
    def __init__(self, rate_limit: int = 8):
        super().__init__(rate_limit)
        self.base_url = "https://www.indeed.com/jobs"
        self.ua = UserAgent()
    
    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 100
    ) -> List[RawJobData]:
        """Search Indeed jobs"""
        
        jobs = []
        start = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while len(jobs) < max_results:
                params = {
                    "q": query,
                    "l": location or "",
                    "start": start,
                    "fromage": "1"  # Last 1 day
                }
                
                headers = {
                    "User-Agent": self.ua.random,
                    "Accept": "text/html",
                }
                
                try:
                    response = await client.get(
                        self.base_url,
                        params=params,
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        print(f"Indeed: Status {response.status_code}")
                        break
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='job_seen_beacon')
                    
                    if not job_cards:
                        break
                    
                    for card in job_cards:
                        try:
                            title_elem = card.find('h2', class_='jobTitle')
                            company_elem = card.find('span', class_='companyName')
                            location_elem = card.find('div', class_='companyLocation')
                            link_elem = card.find('a', href=True)
                            
                            if not all([title_elem, company_elem, link_elem]):
                                continue
                            
                            job_id = link_elem.get('data-jk', '')
                            job_url = f"https://www.indeed.com/viewjob?jk={job_id}"
                            
                            jobs.append(RawJobData(
                                title=title_elem.get_text(strip=True),
                                company=company_elem.get_text(strip=True),
                                location=location_elem.get_text(strip=True) if location_elem else None,
                                description="",
                                url=job_url,
                                source="indeed",
                                source_category="job_board",
                                external_id=job_id
                            ))
                            
                        except Exception as e:
                            print(f"Error parsing Indeed job card: {e}")
                            continue
                    
                    start += 10
                    await self.rate_limit_delay()
                    
                except Exception as e:
                    print(f"Error fetching Indeed jobs: {e}")
                    break
        
        return jobs[:max_results]
    
    async def get_job_details(self, job_url: str) -> Optional[RawJobData]:
        """Get Indeed job description"""
        
        headers = {"User-Agent": self.ua.random}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(job_url, headers=headers)
                
                if response.status_code != 200:
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                description_elem = soup.find('div', id='jobDescriptionText')
                description = description_elem.get_text(separator='\n', strip=True) if description_elem else ""
                
                return RawJobData(
                    title="",
                    company="",
                    description=description,
                    url=job_url,
                    source="indeed",
                    source_category="job_board",
                    raw_html=response.text
                )
                
            except Exception as e:
                print(f"Error fetching Indeed job details: {e}")
                return None
