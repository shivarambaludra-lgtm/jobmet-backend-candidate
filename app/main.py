from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import engine, Base
from app.core.monitoring import init_sentry
from app.core.rate_limiter import limiter
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.error_handler import (
    validation_exception_handler,
    http_exception_handler,
    database_exception_handler,
    general_exception_handler
)
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Initialize monitoring
init_sentry()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="3.0.0",
    description="JobMet.ai Backend API - Production Ready"
)

# Add rate limiter
app.state.limiter = limiter

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Import routers
from app.api.v1 import (
    auth, profile, search, bookmarks,
    saved_searches, applications, recommendations, analytics, monitoring
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(profile.router, prefix=settings.API_V1_PREFIX, tags=["profile"])
app.include_router(search.router, prefix=settings.API_V1_PREFIX, tags=["search"])
app.include_router(bookmarks.router, prefix=settings.API_V1_PREFIX, tags=["bookmarks"])
app.include_router(saved_searches.router, prefix=settings.API_V1_PREFIX, tags=["saved_searches"])
app.include_router(applications.router, prefix=settings.API_V1_PREFIX, tags=["applications"])
app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX, tags=["recommendations"])
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX, tags=["analytics"])
app.include_router(monitoring.router, prefix=settings.API_V1_PREFIX, tags=["monitoring"])

@app.get("/")
async def root():
    return {
        "message": "JobMet.ai Backend API",
        "version": "3.0.0",
        "status": "production",
        "features": [
            "Multi-source job search",
            "Agentic RAG filtering",
            "Real-time WebSocket updates",
            "Background job processing",
            "Caching & rate limiting",
            "Error tracking & monitoring"
        ]
    }

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    from app.utils.logger import logger
    logger.info("🚀 JobMet Backend starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

@app.on_event("shutdown")
async def shutdown_event():
    from app.utils.logger import logger
    logger.info("👋 JobMet Backend shutting down...")

# WebSocket endpoint
from fastapi import WebSocket, WebSocketDisconnect
from app.services.websocket_manager import ws_manager

@app.websocket("/ws/search/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time search updates"""
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
