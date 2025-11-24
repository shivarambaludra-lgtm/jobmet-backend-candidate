from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.job_posting import JobPosting, SearchResult
from app.api.v1.auth import get_current_user
from app.schemas.query_models import SearchRequest, EnrichedQuery
from app.schemas.search_models import SearchResponse, JobResult
from app.services.crawler.crawler_orchestrator import CrawlerOrchestrator
from app.services.job_extractor import JobDataExtractor
from app.services.filtering.categorization import JobCategorizer
from app.workflows.filtering_graph import build_filtering_graph, FilterState
from app.services.query_parser import QueryParserService
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.query_enrichment import QueryEnrichmentService
from app.core.config import settings
import redis
from app.services.websocket_manager import ws_manager
from app.services.filter_generator import DynamicFilterGenerator
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

# Initialize services
_query_parser = None
_kg_service = None
_enrichment_service = None
_crawler_orchestrator = None
_job_extractor = None
_categorizer = None
_filtering_graph = None

def init_search_services():
    """Initialize all search-related services"""
    global _query_parser, _kg_service, _enrichment_service
    global _crawler_orchestrator, _job_extractor, _categorizer, _filtering_graph
    
    try:
        # Week 3-4 services
        _query_parser = QueryParserService(openai_api_key=settings.OPENAI_API_KEY)
        _kg_service = KnowledgeGraphService(
            settings.NEO4J_URI,
            settings.NEO4J_USER,
            settings.NEO4J_PASSWORD
        )
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        _enrichment_service = QueryEnrichmentService(
            _query_parser,
            _kg_service,
            redis_client
        )
        
        # Week 5-6 services
        _crawler_orchestrator = CrawlerOrchestrator()
        _job_extractor = JobDataExtractor(openai_api_key=settings.OPENAI_API_KEY)
        _categorizer = JobCategorizer()
        _filtering_graph = build_filtering_graph()
        
        logger.info("✓ All search services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search services: {e}")
        raise

@router.post("/parse", response_model=EnrichedQuery)
async def parse_search_query(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Parse and enrich a natural language search query"""
    
    # Get candidate profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Build profile context
    profile_context = {
        "skills": [s["name"] for s in (profile.skills or [])],
        "years_experience": profile.years_experience,
        "location": profile.location,
        "visa_status": profile.visa_status,
        "education": profile.education
    }
    
    # Parse and enrich query
    enriched_query = await _enrichment_service.process_query(
        request.query,
        profile_context
    )
    
    return enriched_query

@router.post("/jobs", response_model=SearchResponse)
async def search_jobs_full(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Full job search with web crawling + filtering
    
    Pipeline:
    1. Parse & enrich query (Week 3-4)
    2. Crawl multiple sources (Week 5-6)
    3. Extract structured data with LLM
    4. Apply 5-stage filtering pipeline
    5. Categorize and score results
    6. Cache for future queries
    """
    
    start_time = time.time()
    user_id_str = str(current_user.id)
    
    # Get candidate profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Build profile context
    profile_context = {
        "skills": [s.get("name") for s in (profile.skills or [])],
        "years_experience": profile.years_experience or 0,
        "location": profile.location,
        "visa_status": profile.visa_status,
        "education": profile.education
    }
    
    # Check cache
    query_hash = hashlib.md5(
        (request.query + json.dumps(profile_context, sort_keys=True)).encode()
    ).hexdigest()
    
    cached_result = db.query(SearchResult).filter(
        SearchResult.query_hash == query_hash,
        SearchResult.expires_at > datetime.utcnow()
    ).first()
    
    if cached_result:
        logger.info(f"✓ Cache hit for query: {request.query}")
        return _build_response_from_cache(cached_result, db)
    
    logger.info(f"Starting job search for: {request.query}")
    
    # WebSocket Update: Starting
    await ws_manager.send_search_update(
        user_id_str,
        "started",
        {"message": "Starting job search...", "query": request.query}
    )
    
    # Step 1: Parse and enrich query
    enriched_query = await _enrichment_service.process_query(
        request.query,
        profile_context
    )
    logger.info(f"✓ Query enriched: {enriched_query.original_query.job_title}")
    
    # WebSocket Update: Query parsed
    await ws_manager.send_search_update(
        user_id_str,
        "query_parsed",
        {
            "job_title": enriched_query.original_query.job_title,
            "skills": enriched_query.original_query.skills_required,
            "related_skills": enriched_query.related_skills[:5] if enriched_query.related_skills else []
        }
    )
    
    # Step 2: Crawl jobs from multiple sources
    job_title = enriched_query.original_query.job_title
    location = enriched_query.original_query.location
    
    # WebSocket Update: Crawling started
    await ws_manager.send_search_update(
        user_id_str,
        "crawling",
        {"message": "Searching job boards and career pages..."}
    )
    
    raw_jobs_by_source = await _crawler_orchestrator.search_all_sources(
        query=job_title,
        location=location,
        max_results_per_source=100
    )
    
    # Combine all sources
    all_raw_jobs = []
    for source, jobs in raw_jobs_by_source.items():
        all_raw_jobs.extend(jobs)
    
    all_raw_jobs = _crawler_orchestrator.deduplicate_jobs(all_raw_jobs)
    logger.info(f"✓ Crawled {len(all_raw_jobs)} unique jobs")
    
    # WebSocket Update: Crawling complete
    await ws_manager.send_search_update(
        user_id_str,
        "crawling_complete",
        {
            "total_jobs": len(all_raw_jobs),
            "sources": {source: len(jobs) for source, jobs in raw_jobs_by_source.items()}
        }
    )
    
    # Step 3: Enrich with descriptions (limit to 50 for performance)
    enriched_raw_jobs = await _crawler_orchestrator.enrich_job_details(
        all_raw_jobs[:50]
    )
    logger.info(f"✓ Enriched {len(enriched_raw_jobs)} job descriptions")
    
    # WebSocket Update: Extracting data
    await ws_manager.send_search_update(
        user_id_str,
        "extracting",
        {"message": f"Analyzing {len(enriched_raw_jobs)} job descriptions..."}
    )
    
    # Step 4: Extract structured data with LLM
    job_data_list = []
    for raw_job in enriched_raw_jobs:
        try:
            job_data = await _job_extractor.extract(raw_job)
            job_data_list.append(job_data)
        except Exception as e:
            logger.warning(f"Failed to extract job data: {e}")
            continue
    
    logger.info(f"✓ Extracted structured data from {len(job_data_list)} jobs")
    
    # WebSocket Update: Filtering
    await ws_manager.send_search_update(
        user_id_str,
        "filtering",
        {"message": "Filtering and scoring jobs..."}
    )
    
    # Step 5: Apply 5-stage filtering pipeline
    filter_state: FilterState = {
        "enriched_query": enriched_query,
        "candidate_profile": profile_context,
        "jobs": job_data_list,
        "filtered_jobs": [],
        "filter_stage": "start",
        "rejection_reasons": {}
    }
    
    final_state = _filtering_graph.invoke(filter_state)
    filtered_jobs = final_state["filtered_jobs"]
    logger.info(f"✓ Filtered to {len(filtered_jobs)} relevant jobs")
    
    # Step 6: Categorize into 3 buckets
    # Convert dicts to objects for categorizer
    class JobObject:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    job_objects = [JobObject(job) for job in filtered_jobs]
    categorized = _categorizer.categorize(job_objects)
    
    logger.info(f"✓ Categorized: {len(categorized['job_boards'])} job boards, "
                f"{len(categorized['career_pages'])} career pages, "
                f"{len(categorized['hiring_posts'])} hiring posts")
    
    # Step 7: Generate dynamic filters
    filter_generator = DynamicFilterGenerator()
    dynamic_filters = filter_generator.generate_filters(job_objects)
    logger.info(f"✓ Generated dynamic filters")
    
    # Step 8: Save to database (background task)
    background_tasks.add_task(
        _save_jobs_to_db,
        db,
        filtered_jobs,
        query_hash,
        request.query,
        enriched_query,
        str(current_user.id)
    )
    
    processing_time = time.time() - start_time
    logger.info(f"✓ Search completed in {processing_time:.2f}s")
    
):
    """Save jobs and search results to database (background task)"""
    try:
        # Save job postings
        for job_data in jobs:
            existing = db.query(JobPosting).filter(
                JobPosting.url == job_data.get("url")
            ).first()
            
            if not existing:
                job_posting = JobPosting(
                    title=job_data.get("title"),
                    company=job_data.get("company"),
                    location=job_data.get("location"),
                    description=job_data.get("description"),
                    skills=job_data.get("skills"),
                    years_experience_min=job_data.get("years_experience_min"),
                    years_experience_max=job_data.get("years_experience_max"),
                    education_required=job_data.get("education_required"),
                    salary_min=job_data.get("salary_min"),
                    salary_max=job_data.get("salary_max"),
                    visa_sponsorship=job_data.get("visa_sponsorship", False),
                    requires_citizenship=job_data.get("requires_citizenship", False),
                    work_authorization=job_data.get("work_authorization"),
                    source=job_data.get("source"),
                    source_category=job_data.get("source_category"),
                    url=job_data.get("url"),
                    external_id=job_data.get("external_id"),
                    posted_date=job_data.get("posted_date"),
                    raw_html=job_data.get("raw_html")
                )
                db.add(job_posting)
        
        # Save search result
        search_result = SearchResult(
            query_hash=query_hash,
            original_query=original_query,
            parsed_query=enriched_query.original_query.model_dump(),
            enriched_query=enriched_query.model_dump(),
            job_posting_ids=[{"url": j.get("url"), "score": j.get("match_score", 0)} for j in jobs],
            total_results=len(jobs),
            candidate_id=candidate_id,
            expires_at=datetime.utcnow() + timedelta(hours=24),
            processing_time=0
        )
        db.add(search_result)
        db.commit()
        logger.info(f"✓ Saved {len(jobs)} jobs to database")
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        db.rollback()

def _build_response_from_cache(cached: SearchResult, db: Session) -> SearchResponse:
    """Build response from cached search result"""
    job_urls = [item["url"] for item in cached.job_posting_ids]
    jobs = db.query(JobPosting).filter(JobPosting.url.in_(job_urls)).all()
    
    # Convert to dicts for categorizer
    job_dicts = []
    for job in jobs:
        job_dict = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "skills": job.skills,
            "years_experience_min": job.years_experience_min,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "visa_sponsorship": job.visa_sponsorship,
            "source": job.source,
            "source_category": job.source_category,
            "url": job.url,
            "posted_date": job.posted_date,
            "match_score": next((item["score"] for item in cached.job_posting_ids if item["url"] == job.url), 0)
        }
        job_dicts.append(job_dict)
    
    # Categorize
    class JobObject:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    job_objects = [JobObject(job) for job in job_dicts]
    categorized = _categorizer.categorize(job_objects)
    
    return SearchResponse(
        query=cached.original_query,
        parsed_query=cached.parsed_query,
        total_results=cached.total_results,
        job_boards=[_job_dict_to_result(vars(obj)) for obj in categorized["job_boards"]],
        career_pages=[_job_dict_to_result(vars(obj)) for obj in categorized["career_pages"]],
        hiring_posts=[_job_dict_to_result(vars(obj)) for obj in categorized["hiring_posts"]],
        processing_time=0.1  # Cached response
    )
