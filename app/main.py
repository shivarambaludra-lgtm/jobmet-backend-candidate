from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.api.v1.routes_candidate import router as candidate_router
from app.api.v1.routes_jobs import router as jobs_router
from app.core.logging_config import setup_logging
import logging
import os

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add startup event
@app.on_event("startup")
async def startup_event():
    logger.info("JobMet.AI API starting up...")
    logger.info(f"OpenAI configured: {bool(settings.OPENAI_API_KEY)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("JobMet.AI API shutting down...")

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        # Test OpenAI key is set
        has_openai = bool(os.getenv("OPENAI_API_KEY"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "openai_configured": has_openai
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

app.include_router(
    candidate_router,
    prefix=f"{settings.API_V1_PREFIX}/candidate",
    tags=["candidate"],
)

app.include_router(
    jobs_router,
    prefix=f"{settings.API_V1_PREFIX}/jobs",
    tags=["jobs"],
)
