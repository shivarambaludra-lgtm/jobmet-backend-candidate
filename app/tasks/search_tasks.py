from app.core.celery_app import celery_app
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.job_posting import JobPosting
import asyncio
from typing import Dict, Any

@celery_app.task(name="app.tasks.search_tasks.run_background_search", bind=True)
def run_background_search(self, query: str, user_id: str, profile_data: dict) -> Dict[str, Any]:
    """Run job search in background (for saved searches)"""
    
    db = SessionLocal()
    
    try:
        self.update_state(state="PROGRESS", meta={"stage": "initializing"})
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            _async_background_search(query, user_id, profile_data, db, self)
        )
        
        return {
            "status": "success",
            "total_jobs": result["total_jobs"],
            "user_id": user_id
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id
        }
    finally:
        db.close()

async def _async_background_search(
    query: str, 
    user_id: str, 
    profile_data: dict, 
    db: Session,
    task
) -> Dict[str, Any]:
    """Async search logic with progress updates"""
    
    from app.services.crawler.crawler_orchestrator import CrawlerOrchestrator
    from app.services.job_extractor import JobDataExtractor
    from app.workflows.filtering_graph import build_filtering_graph
    from app.schemas.query_models import EnrichedQuery, ParsedQuery
    
    task.update_state(state="PROGRESS", meta={"stage": "crawling"})
    
    crawler = CrawlerOrchestrator()
    extractor = JobDataExtractor(openai_api_key=settings.OPENAI_API_KEY)
    filtering_graph = build_filtering_graph()
    
    # Crawl jobs
    raw_jobs_by_source = await crawler.search_all_sources(
        query=query,
        max_results_per_source=50
    )
    
    all_raw_jobs = []
    for source, jobs in raw_jobs_by_source.items():
        all_raw_jobs.extend(jobs)
    
    task.update_state(state="PROGRESS", meta={
        "stage": "extracting",
        "total_jobs": len(all_raw_jobs)
    })
    
    # Extract structured data
    job_postings = []
    for idx, raw_job in enumerate(all_raw_jobs[:50]):
        try:
            job_posting = await extractor.extract(raw_job)
            job_postings.append(job_posting)
            
            if idx % 10 == 0:
                task.update_state(state="PROGRESS", meta={
                    "stage": "extracting",
                    "progress": f"{idx}/{len(all_raw_jobs[:50])}"
                })
        except Exception as e:
            print(f"Error extracting job: {e}")
    
    task.update_state(state="PROGRESS", meta={"stage": "filtering"})
    
    # Filter jobs
    enriched_query = EnrichedQuery(
        original_query=ParsedQuery(job_title=query),
        expanded_job_titles=[],
        related_skills=[],
        sponsor_companies=[],
        education_alternatives=[]
    )
    
    filter_state = {
        "enriched_query": enriched_query,
        "candidate_profile": profile_data,
        "jobs": job_postings,
        "filtered_jobs": [],
        "filter_stage": "start",
        "rejection_reasons": {}
    }
    
    final_state = filtering_graph.invoke(filter_state)
    
    return {
        "total_jobs": len(final_state["filtered_jobs"]),
        "filtered_jobs": final_state["filtered_jobs"]
    }

@celery_app.task(name="app.tasks.search_tasks.enrich_job_descriptions")
def enrich_job_descriptions(job_ids: list) -> Dict[str, Any]:
    """Enrich job descriptions in background"""
    
    db = SessionLocal()
    
    try:
        jobs = db.query(JobPosting).filter(JobPosting.id.in_(job_ids)).all()
        
        if not jobs:
            return {"status": "success", "enriched": 0}
        
        from app.services.crawler.crawler_orchestrator import CrawlerOrchestrator
        from app.services.crawler.base_crawler import RawJobData
        
        crawler = CrawlerOrchestrator()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        raw_jobs = [
            RawJobData(
                title=j.title,
                company=j.company,
                location=j.location,
                description=j.description or "",
                url=j.url,
                source=j.source,
                source_category=j.source_category
            )
            for j in jobs
        ]
        
        enriched_jobs = loop.run_until_complete(
            crawler.enrich_job_details(raw_jobs)
        )
        
        for enriched_job in enriched_jobs:
            db_job = next((j for j in jobs if j.url == enriched_job.url), None)
            if db_job and enriched_job.description:
                db_job.description = enriched_job.description
                db_job.raw_html = enriched_job.raw_html
        
        db.commit()
        
        return {"status": "success", "enriched": len(enriched_jobs)}
    
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
