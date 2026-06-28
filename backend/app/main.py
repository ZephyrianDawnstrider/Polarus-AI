from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import logger, setup_logging

setup_logging()
logger.info("Server starting")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Log application lifecycle events."""

    try:
        yield
    finally:
        logger.info("Server shutdown")


app: FastAPI = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Research Operating System",
    lifespan=lifespan,
)

app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Polarus AI",
        "version": settings.APP_VERSION,
    }
