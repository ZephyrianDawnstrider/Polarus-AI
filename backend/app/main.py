from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import logger

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Research Operating System",
)

app.include_router(health_router)
logger.info("Polarus AI Started")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Polarus AI",
        "version": settings.APP_VERSION,
    }
