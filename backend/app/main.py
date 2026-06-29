from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.middleware.exception_handler import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.middleware.request_id import RequestIDMiddleware

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

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_middleware(RequestIDMiddleware)

v1_router: APIRouter = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(health_router)
app.include_router(v1_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Polarus AI",
        "version": settings.APP_VERSION,
    }
