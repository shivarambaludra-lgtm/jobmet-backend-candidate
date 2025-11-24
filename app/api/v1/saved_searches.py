from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.saved_search import SavedSearch
from app.models.candidate_profile import CandidateProfile
from app.api.v1.auth import get_current_user
from app.schemas.query_models import SearchRequest
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/saved-searches", tags=["saved_searches"])

class SavedSearchCreate(BaseModel):
    name: str
    query: str
    parsed_query: Optional[dict] = None
    email_alerts: bool = False
    alert_frequency: str = "daily"  # "daily", "weekly", "never"

class SavedSearchUpdate(BaseModel):
    name: Optional[str] = None
    email_alerts: Optional[bool] = None
    alert_frequency: Optional[str] = None
    is_active: Optional[bool] = None

class SavedSearchResponse(BaseModel):
    id: str
    name: str
    query: str
    email_alerts: bool
    alert_frequency: str
    last_run_at: Optional[datetime]
    new_jobs_count: int
    created_at: datetime
    is_active: bool

@router.post("/", status_code=201)
async def create_saved_search(
    search_data: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a search query for later re-use"""
    
    # Check if name already exists for this user
    existing = db.query(SavedSearch).filter(
        SavedSearch.user_id == current_user.id,
        SavedSearch.name == search_data.name,
        SavedSearch.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"You already have a saved search named '{search_data.name}'"
        )
    
    # Create saved search
    saved_search = SavedSearch(
        user_id=current_user.id,
        name=search_data.name,
        query=search_data.query,
        parsed_query=search_data.parsed_query,
        email_alerts=search_data.email_alerts,
        alert_frequency=search_data.alert_frequency
    )
    db.add(saved_search)
    db.commit()
    db.refresh(saved_search)
    
    return {
        "id": str(saved_search.id),
        "message": f"Search '{search_data.name}' saved successfully"
    }

@router.get("/", response_model=List[SavedSearchResponse])
async def get_saved_searches(
    skip: int = 0,
    limit: int = 50,
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved searches"""
    
    query = db.query(SavedSearch).filter(
        SavedSearch.user_id == current_user.id
    )
    
    if not include_inactive:
        query = query.filter(SavedSearch.is_active == True)
    
    searches = query.order_by(SavedSearch.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        SavedSearchResponse(
            id=str(s.id),
            name=s.name,
            query=s.query,
            email_alerts=s.email_alerts,
            alert_frequency=s.alert_frequency,
            last_run_at=s.last_run_at,
            new_jobs_count=s.new_jobs_count,
            created_at=s.created_at,
            is_active=s.is_active
        )
        for s in searches
    ]

@router.get("/{search_id}")
async def get_saved_search(
    search_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific saved search"""
    
    saved_search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not saved_search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    return {
        "id": str(saved_search.id),
        "name": saved_search.name,
        "query": saved_search.query,
        "parsed_query": saved_search.parsed_query,
        "email_alerts": saved_search.email_alerts,
        "alert_frequency": saved_search.alert_frequency,
        "last_run_at": saved_search.last_run_at,
        "new_jobs_count": saved_search.new_jobs_count,
        "created_at": saved_search.created_at,
        "is_active": saved_search.is_active
    }

@router.patch("/{search_id}")
async def update_saved_search(
    search_id: UUID,
    update_data: SavedSearchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a saved search"""
    
    saved_search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not saved_search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    # Update fields
    if update_data.name is not None:
        saved_search.name = update_data.name
    if update_data.email_alerts is not None:
        saved_search.email_alerts = update_data.email_alerts
    if update_data.alert_frequency is not None:
        saved_search.alert_frequency = update_data.alert_frequency
    if update_data.is_active is not None:
        saved_search.is_active = update_data.is_active
    
    db.commit()
    
    return {"message": "Saved search updated successfully"}

@router.post("/{search_id}/run")
async def run_saved_search(
    search_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Re-run a saved search"""
    
    saved_search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not saved_search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    # Import here to avoid circular dependency
    from app.api.v1.search import search_jobs_full
    
    # Create search request
    search_request = SearchRequest(query=saved_search.query)
    
    # Run search (this will use the full pipeline)
    try:
        results = await search_jobs_full(search_request, background_tasks, current_user, db)
        
        # Update saved search
        saved_search.last_run_at = datetime.utcnow()
        saved_search.new_jobs_count = results.total_results
        db.commit()
        
        return {
            "message": "Search completed successfully",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.delete("/{search_id}")
async def delete_saved_search(
    search_id: UUID,
    hard_delete: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a saved search (soft delete by default)"""
    
    saved_search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()
    
    if not saved_search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    if hard_delete:
        db.delete(saved_search)
        message = "Saved search permanently deleted"
    else:
        saved_search.is_active = False
        message = "Saved search deactivated"
    
    db.commit()
    
    return {"message": message}

@router.get("/stats/summary")
async def get_saved_search_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get saved search statistics"""
    
    total_active = db.query(SavedSearch).filter(
        SavedSearch.user_id == current_user.id,
        SavedSearch.is_active == True
    ).count()
    
    with_alerts = db.query(SavedSearch).filter(
        SavedSearch.user_id == current_user.id,
        SavedSearch.is_active == True,
        SavedSearch.email_alerts == True
    ).count()
    
    return {
        "total_active": total_active,
        "with_email_alerts": with_alerts
    }
