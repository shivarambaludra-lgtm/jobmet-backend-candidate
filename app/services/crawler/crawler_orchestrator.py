from app.services.crawler.base_crawler import RawJobData
from app.services.crawler.linkedin_crawler import LinkedInCrawler
from app.services.crawler.indeed_crawler import IndeedCrawler
from app.services.crawler.career_page_crawler import CareerPageCrawler
from typing import List, Dict, Optional
import asyncio

class CrawlerOrchestrator:
    """Orchestrate multiple crawlers in parallel"""
    
    def __init__(self):
        self.crawlers = {
            "linkedin": LinkedInCrawler(),
            "indeed": IndeedCrawler(),
            "career_pages": CareerPageCrawler()
        }
    
    async def search_all_sources(
        self,
        query: str,
        location: Optional[str] = None,
        max_results_per_source: int = 100
    ) -> Dict[str, List[RawJobData]]:
        """Search all job sources in parallel"""
        
        tasks = []
        for source_name, crawler in self.crawlers.items():
            task = crawler.search_jobs(query, location, max_results_per_source)
            tasks.append((source_name, task))
        
        results = {}
        for source_name, task in tasks:
            try:
                jobs = await task
                results[source_name] = jobs
                print(f"✓ {source_name}: Found {len(jobs)} jobs")
            except Exception as e:
                print(f"✗ {source_name}: Error - {e}")
                results[source_name] = []
        
        return results
    
    async def enrich_job_details(self, jobs: List[RawJobData]) -> List[RawJobData]:
        """Fetch detailed descriptions for jobs (parallel)"""
        
        enriched = []
        batch_size = 10
        
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i+batch_size]
            tasks = []
            
            for job in batch:
                crawler = self.crawlers.get(job.source)
                if crawler:
                    tasks.append(self._enrich_single_job(crawler, job))
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            enriched.extend([r for r in batch_results if not isinstance(r, Exception)])
            
            await asyncio.sleep(1)
        
        return enriched
    
    async def _enrich_single_job(self, crawler, job: RawJobData) -> RawJobData:
        try:
            details = await crawler.get_job_details(job.url)
            if details and details.description:
                job.description = details.description
                job.raw_html = details.raw_html
        except Exception as e:
            print(f"Error enriching job {job.url}: {e}")
        
        return job
    
    def deduplicate_jobs(self, jobs: List[RawJobData]) -> List[RawJobData]:
        """Remove duplicate jobs based on URL"""
        
        seen_urls = set()
        unique_jobs = []
        
        for job in jobs:
            if job.url not in seen_urls:
                seen_urls.add(job.url)
                unique_jobs.append(job)
        
        return unique_jobs
