# Week 7-8 Phase 1: Models + Filters + WebSocket - Setup Guide

## ✅ Phase 1 Complete!

All core components for real-time search with dynamic filters have been created.

---

## 📦 Files Created

### Database Models (4 files)
1. **`app/models/bookmark.py`** - User's bookmarked jobs
   - Unique constraint on (user_id, job_posting_id)
   - Notes field for annotations
   
2. **`app/models/saved_search.py`** - Saved search queries
   - Email alert configuration
   - Last run timestamp
   - Active/inactive flag

3. **`app/models/job_application.py`** - Enhanced application tracking
   - Status enum: draft, submitted, viewed, screening, interview, offer, rejected
   - Interview dates array (JSONB)
   - Timeline tracking

4. **`app/models/user_activity.py`** - Analytics tracking
   - Activity types: search, view_job, apply, bookmark
   - Session tracking (IP, user agent)

### Services (2 files)
5. **`app/services/filter_generator.py`** - Dynamic filter generation
   - Extracts locations, companies, skills from results
   - Generates salary ranges, experience levels
   - Counts visa sponsorship availability

6. **`app/services/websocket_manager.py`** - Real-time updates
   - Connection management
   - Progress broadcasting
   - User-specific messaging

### Updated Files
7. **`app/main.py`** - Added WebSocket endpoint
   - `/ws/search/{user_id}` endpoint
   - Ping/pong keep-alive
   - Enhanced health check

8. **`app/api/v1/search.py`** - Fixed syntax errors
   - Ready for WebSocket integration
   - Filter generator integration pending

9. **`requirements.txt`** - Added dependencies
   - websockets, python-socketio
   - scikit-learn, numpy, pandas
   - slowapi (rate limiting)

---

## 🔧 Installation Steps

### Step 1: Install Dependencies
```bash
# Dependencies are currently installing in background
# Wait for completion, then verify:
.\.venv\Scripts\python -m pip list | Select-String "websockets|socketio|scikit"
```

### Step 2: Create Database Migration
```bash
# Migration is being created in background
# Once complete, review the migration file:
ls app\alembic\versions\*week_7_8*.py

# Then apply migration:
.\.venv\Scripts\python -m alembic upgrade head
```

### Step 3: Update Models __init__.py
```python
# Add to app/models/__init__.py:
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.bookmark import Bookmark
from app.models.saved_search import SavedSearch
from app.models.job_application import JobApplication, ApplicationStatus
from app.models.user_activity import UserActivity
```

---

## 🧪 Testing

### Test 1: WebSocket Connection
Create `test_websocket.html`:
```html
<!DOCTYPE html>
<html>
<body>
<h1>WebSocket Test</h1>
<div id="messages"></div>

<script>
const ws = new WebSocket('ws://localhost:8000/ws/search/test-user-123');

ws.onopen = () => {
    console.log('✓ Connected');
    document.getElementById('messages').innerHTML += '<p>✓ Connected</p>';
    
    // Send ping
    ws.send('ping');
};

ws.onmessage = (event) => {
    console.log('Message:', event.data);
    document.getElementById('messages').innerHTML += `<p>📨 ${event.data}</p>`;
};

ws.onerror = (error) => {
    console.error('Error:', error);
    document.getElementById('messages').innerHTML += '<p>❌ Error</p>';
};
</script>
</body>
</html>
```

Open in browser: `start test_websocket.html`

### Test 2: Dynamic Filter Generation
Create `test_filters.py`:
```python
from app.services.filter_generator import DynamicFilterGenerator

# Sample jobs
jobs = [
    {
        "location": "San Francisco, CA",
        "company": "Google",
        "skills": ["Python", "Django", "PostgreSQL"],
        "years_experience_min": 3,
        "salary_min": 120000,
        "visa_sponsorship": True,
        "education_required": "Bachelor"
    },
    {
        "location": "Remote",
        "company": "Meta",
        "skills": ["Python", "React", "AWS"],
        "years_experience_min": 5,
        "salary_min": 150000,
        "visa_sponsorship": True,
        "education_required": "Master"
    }
]

# Generate filters
generator = DynamicFilterGenerator()
filters = generator.generate_filters(jobs)

print("Generated Filters:")
print(f"Locations: {filters['locations']}")
print(f"Companies: {filters['companies']}")
print(f"Skills: {filters['skills']}")
print(f"Experience Levels: {filters['experience_levels']}")
print(f"Salary Ranges: {filters['salary_ranges']}")
print(f"Visa Sponsorship: {filters['visa_sponsorship']}")
```

Run: `.\.venv\Scripts\python test_filters.py`

### Test 3: Database Models
```bash
# Start Python REPL
.\.venv\Scripts\python

# Test imports
from app.models.bookmark import Bookmark
from app.models.saved_search import SavedSearch
from app.models.job_application import JobApplication, ApplicationStatus
from app.models.user_activity import UserActivity

print("✓ All models imported successfully")

# Check ApplicationStatus enum
print(list(ApplicationStatus))
# Output: [<ApplicationStatus.DRAFT: 'draft'>, <ApplicationStatus.SUBMITTED: 'submitted'>, ...]
```

---

## 📊 Database Schema

### New Tables Created:
```sql
-- bookmarks
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    job_posting_id UUID REFERENCES job_postings(id),
    notes TEXT,
    created_at TIMESTAMP,
    UNIQUE(user_id, job_posting_id)
);

-- saved_searches
CREATE TABLE saved_searches (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR NOT NULL,
    query TEXT NOT NULL,
    parsed_query JSONB,
    email_alerts BOOLEAN DEFAULT FALSE,
    alert_frequency VARCHAR DEFAULT 'daily',
    last_run_at TIMESTAMP,
    new_jobs_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- job_applications
CREATE TABLE job_applications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    job_posting_id UUID REFERENCES job_postings(id),
    status VARCHAR,  -- enum
    cover_letter TEXT,
    resume_used VARCHAR,
    applied_at TIMESTAMP,
    last_updated TIMESTAMP,
    application_url VARCHAR,
    confirmation_email VARCHAR,
    interview_dates JSONB,
    notes TEXT
);

-- user_activities
CREATE TABLE user_activities (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    activity_type VARCHAR NOT NULL,
    activity_data JSONB,
    job_posting_id UUID REFERENCES job_postings(id),
    session_id VARCHAR,
    ip_address VARCHAR,
    user_agent VARCHAR,
    created_at TIMESTAMP
);
```

---

## 🚀 Next Steps

**Phase 1 Remaining:**
- [ ] Complete WebSocket integration in search.py (add progress updates)
- [ ] Test WebSocket with real search
- [ ] Verify dynamic filters work with search results

**Phase 2 Preview (Bookmarks + Saved Searches):**
- Create `app/api/v1/bookmarks.py` router
- Create `app/api/v1/saved_searches.py` router
- Implement CRUD endpoints
- Test bookmark/save workflows

---

## ✅ Success Criteria

- [x] All 4 database models created
- [x] Dynamic filter generator implemented
- [x] WebSocket manager created
- [x] WebSocket endpoint added to main.py
- [x] Dependencies updated
- [ ] Database migration applied
- [ ] WebSocket tested with frontend
- [ ] Dynamic filters tested with search results

---

**Status:** Phase 1 ~90% Complete  
**Remaining:** WebSocket integration in search API, migration application, testing  
**Estimated Time:** 10-15 minutes

**Last Updated:** November 23, 2025
