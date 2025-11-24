# Week 5-6 Setup & Testing Guide

## 🎯 Implementation Complete!

All 13 files for Week 5-6 Multi-Source Web Crawler have been created.

---

## 📦 Installation Steps

### Step 1: Install Python Dependencies
```bash
.\.venv\Scripts\python -m pip install playwright fake-useragent aiolimiter tenacity dateparser
```

### Step 2: Install Playwright Browsers
```bash
.\.venv\Scripts\playwright install chromium
```

### Step 3: Create Database Migration
```bash
.\.venv\Scripts\python -m alembic revision --autogenerate -m "add_job_posting_and_search_result_tables"
```

### Step 4: Review Migration File
Check `app/alembic/versions/XXXXX_add_job_posting_and_search_result_tables.py`

Should create:
- `job_postings` table (20+ columns)
- `search_results` table (10+ columns)

### Step 5: Apply Migration
```bash
.\.venv\Scripts\python -m alembic upgrade head
```

### Step 6: Start Services
```bash
# Start Docker services (Neo4j, Redis, PostgreSQL)
docker compose up -d

# Verify services are running
docker compose ps
```

### Step 7: Initialize Neo4j
```bash
# Access Neo4j Browser
start http://localhost:7474

# Login: neo4j / jobmet123
# Run: neo4j/init_schema.cypher
# Run: neo4j/seed_data.cypher
```

---

## 🧪 Testing

### Test 1: LinkedIn Crawler
Create `test_linkedin.py`:
```python
from app.services.crawler.linkedin_crawler import LinkedInCrawler
import asyncio

async def test():
    crawler = LinkedInCrawler()
    jobs = await crawler.search_jobs("python developer", "San Francisco", 5)
    print(f"✓ Found {len(jobs)} LinkedIn jobs")
    for job in jobs:
        print(f"  - {job.title} at {job.company}")

asyncio.run(test())
```

Run: `.\.venv\Scripts\python test_linkedin.py`

### Test 2: Crawler Orchestrator
Create `test_orchestrator.py`:
```python
from app.services.crawler.crawler_orchestrator import CrawlerOrchestrator
import asyncio

async def test():
    orchestrator = CrawlerOrchestrator()
    results = await orchestrator.search_all_sources(
        query="software engineer",
        location="Remote",
        max_results_per_source=10
    )
    
    for source, jobs in results.items():
        print(f"✓ {source}: {len(jobs)} jobs")
    
    # Test deduplication
    all_jobs = []
    for jobs in results.values():
        all_jobs.extend(jobs)
    
    unique = orchestrator.deduplicate_jobs(all_jobs)
    print(f"✓ Total: {len(all_jobs)} → Unique: {len(unique)}")

asyncio.run(test())
```

Run: `.\.venv\Scripts\python test_orchestrator.py`

### Test 3: Full Search API
```bash
# Get JWT token
$TOKEN = (curl -X POST "http://localhost:8000/api/v1/auth/login" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=test@example.com&password=testpass123" | ConvertFrom-Json).access_token

# Test search
curl -X POST "http://localhost:8000/api/v1/search/jobs" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"query": "python developer 3+ years remote"}' | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 📊 Expected Results

### Crawler Output:
```
✓ linkedin: Found 10 jobs
✓ indeed: Found 10 jobs
✓ career_pages: Found 0 jobs
✓ Total: 20 → Unique: 18
```

### Filtering Pipeline Output:
```
Filter 1 (Role Match): 50 → 35 jobs
Filter 2 (Experience): 35 → 28 jobs
Filter 3 (Visa): 28 → 20 jobs
Filter 4 (Education): 20 → 18 jobs
Filter 5 (Scoring): Scored 18 jobs
```

### API Response:
```json
{
  "query": "python developer 3+ years remote",
  "total_results": 18,
  "job_boards": [...],
  "career_pages": [...],
  "hiring_posts": [...],
  "processing_time": 45.2
}
```

---

## 🚨 Common Issues

### Issue 1: ModuleNotFoundError: playwright
**Solution:**
```bash
.\.venv\Scripts\python -m pip install playwright
.\.venv\Scripts\playwright install chromium
```

### Issue 2: LinkedIn/Indeed Blocking
**Symptoms:** 403 errors, empty results

**Solutions:**
1. Reduce rate limit in crawlers
2. Use proxies (add to crawler config)
3. Consider official APIs instead

### Issue 3: OpenAI Rate Limits
**Solution:**
```python
# In job_extractor.py, add retry logic
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(3))
async def extract_with_retry(self, raw_job):
    return await self.llm.ainvoke(prompt)
```

### Issue 4: Database Connection Pool Exhausted
**Solution:**
```python
# In app/core/database.py
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=20,  # Increase from default 5
    max_overflow=10
)
```

---

## ✅ Success Criteria

- [ ] All dependencies installed
- [ ] Playwright browsers installed
- [ ] Database migration created and applied
- [ ] Docker services running (Neo4j, Redis, PostgreSQL)
- [ ] Neo4j seeded with knowledge graph data
- [ ] LinkedIn crawler returns 5+ jobs
- [ ] Orchestrator runs multiple crawlers in parallel
- [ ] Filtering pipeline reduces jobs correctly
- [ ] Search API returns categorized results
- [ ] Cache works (second query < 1s)

---

## 📁 Files Created

```
✅ app/services/crawler/__init__.py
✅ app/services/crawler/base_crawler.py
✅ app/services/crawler/linkedin_crawler.py
✅ app/services/crawler/indeed_crawler.py
✅ app/services/crawler/glassdoor_crawler.py
✅ app/services/crawler/career_page_crawler.py
✅ app/services/crawler/crawler_orchestrator.py
✅ app/services/filtering/__init__.py
✅ app/services/filtering/categorization.py
✅ app/services/job_extractor.py
✅ app/prompts/job_extraction.py
✅ app/models/job_posting.py
✅ app/workflows/filtering_graph.py
✅ app/api/v1/search.py (UPDATED)
```

**Total:** 13 files, ~1,200 lines of code

---

## 🎯 Next Steps

1. **Test Each Component** - Run the 3 test scripts above
2. **Database Migration** - Create and apply migration
3. **End-to-End Test** - Test full search API
4. **Performance Tuning** - Optimize slow components
5. **Production Prep** - Add error handling, logging, monitoring

---

## 🚀 Week 7-8 Preview

- Frontend integration (Next.js)
- Dynamic filters (location, salary, company size)
- Real-time search updates
- Job bookmarking & saved searches
- Application tracking

---

**Last Updated:** November 23, 2025  
**Status:** Week 5-6 Implementation Complete ✅  
**Ready for Testing:** Yes
