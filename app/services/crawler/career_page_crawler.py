from app.services.crawler.base_crawler import BaseCrawler, RawJobData
from typing import List, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

class CareerPageCrawler(BaseCrawler):
    """Generic crawler for company career pages"""
    
    def __init__(self, rate_limit: int = 3):
        super().__init__(rate_limit)
    
    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        max_results: int = 100
    ) -> List[RawJobData]:
        """
        Search career pages via Google (placeholder)
        Implement Google Custom Search API or scrape Google
        """
        return []
    
    async def crawl_career_page(self, url: str, keywords: List[str]) -> List[RawJobData]:
        """
        Crawl a specific company career page
        
        Args:
            url: Career page URL
            keywords: Job keywords to filter
        """
        
        jobs = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_timeout(2000)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                job_links = soup.find_all('a', href=True)
                
                for link in job_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    
                    if any(keyword.lower() in text for keyword in keywords):
                        full_url = href if href.startswith('http') else f"{url.rstrip('/')}/{href.lstrip('/')}"
                        
                        jobs.append(RawJobData(
                            title=link.get_text(strip=True),
                            company=self._extract_company_from_url(url),
                            location=None,
                            description="",
                            url=full_url,
                            source="career_page",
                            source_category="career_page"
                        ))
                
            except Exception as e:
                print(f"Error crawling career page {url}: {e}")
            finally:
                await browser.close()
        
        await self.rate_limit_delay()
        return jobs
    
    async def get_job_details(self, job_url: str) -> Optional[RawJobData]:
        """Get job details from career page"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(job_url, timeout=30000)
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                description = ""
                for selector in ['div.job-description', 'div.description', 'article', 'main']:
                    elem = soup.select_one(selector)
                    if elem:
                        description = elem.get_text(separator='\n', strip=True)
                        break
                
                return RawJobData(
                    title="",
                    company="",
                    description=description,
                    url=job_url,
                    source="career_page",
                    source_category="career_page",
                    raw_html=content
                )
                
            except Exception as e:
                print(f"Error getting career page details: {e}")
                return None
            finally:
                await browser.close()
    
    def _extract_company_from_url(self, url: str) -> str:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain.replace('www.', '').split('.')[0].title()
