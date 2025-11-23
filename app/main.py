from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.routes_apply import router as apply_router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(
    apply_router,
    prefix=f"{settings.API_V1_PREFIX}/candidate",
    tags=["candidate-apply"],
)
