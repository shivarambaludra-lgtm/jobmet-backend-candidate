from app.services.crawler.base_crawler import RawJobData
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.prompts.job_extraction import JOB_EXTRACTION_PROMPT
import json
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class JobDataExtractor:
    """Extract structured data from raw job descriptions using LLM"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            api_key=openai_api_key
        )
        
        self.extraction_prompt = ChatPromptTemplate.from_template(JOB_EXTRACTION_PROMPT)
    
    async def extract(self, raw_job: RawJobData):
        """Extract structured data from raw job"""
        
        formatted_prompt = self.extraction_prompt.format(
            title=raw_job.title,
            company=raw_job.company,
            description=raw_job.description[:3000]  # Limit to 3000 chars
        )
        
        try:
            response = await self.llm.ainvoke(formatted_prompt)
            extracted = json.loads(response.content)
        except Exception as e:
            logger.warning(f"LLM extraction failed, using fallback: {e}")
            extracted = self._fallback_extraction(raw_job.description)
        
        # Return dict with extracted data
        return {
            "title": raw_job.title,
            "company": raw_job.company,
            "location": raw_job.location,
            "description": raw_job.description,
            "skills": extracted.get("skills", []),
            "years_experience_min": extracted.get("years_experience_min"),
            "years_experience_max": extracted.get("years_experience_max"),
            "education_required": extracted.get("education_required"),
            "salary_min": extracted.get("salary_min"),
            "salary_max": extracted.get("salary_max"),
            "visa_sponsorship": extracted.get("visa_sponsorship", False),
            "requires_citizenship": extracted.get("requires_citizenship", False),
            "work_authorization": extracted.get("work_authorization", []),
            "source": raw_job.source,
            "source_category": raw_job.source_category,
            "url": raw_job.url,
            "external_id": raw_job.external_id,
            "posted_date": raw_job.posted_date,
            "raw_html": raw_job.raw_html
        }
    
    def _fallback_extraction(self, description: str) -> dict:
        """Rule-based extraction fallback"""
        
        # Extract years of experience
        exp_pattern = r'(\d+)\+?\s*(?:to|-|–)\s*(\d+)?\s*years?'
        exp_match = re.search(exp_pattern, description, re.IGNORECASE)
        years_min = int(exp_match.group(1)) if exp_match else None
        years_max = int(exp_match.group(2)) if exp_match and exp_match.group(2) else None
        
        # Detect visa sponsorship
        visa_keywords = ['sponsorship', 'h1b', 'h-1b', 'visa']
        visa_sponsorship = any(kw in description.lower() for kw in visa_keywords)
        
        # Detect citizenship requirements
        citizenship_keywords = ['us citizen', 'citizenship required', 'must be authorized']
        requires_citizenship = any(kw in description.lower() for kw in citizenship_keywords)
        
        return {
            "skills": [],
            "years_experience_min": years_min,
            "years_experience_max": years_max,
            "visa_sponsorship": visa_sponsorship,
            "requires_citizenship": requires_citizenship,
            "work_authorization": []
        }
