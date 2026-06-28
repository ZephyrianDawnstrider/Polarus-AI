from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.logging import logger


def _request_id(request: Request) -> str:
    """Return the request ID created by RequestIDMiddleware."""

    return getattr(request.state, "request_id", "unknown")


def _error_response(
    *,
    request: Request,
    status_code: int,
    error_type: str,
    message: str,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """Build the standard JSON error response body."""

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
                "request_id": _request_id(request),
                "timestamp": datetime.now(UTC).isoformat(),
            },
        },
        headers=headers,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle expected HTTP errors raised by the API."""

    return _error_response(
        request=request,
        status_code=exc.status_code,
        error_type="HTTPException",
        message=str(exc.detail),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle request validation errors with a consistent JSON response."""

    errors: list[dict[str, Any]] = exc.errors()

    return _error_response(
        request=request,
        status_code=422,
        error_type="RequestValidationError",
        message=str(errors),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions without exposing internal details."""

    logger.exception(
        "Unexpected exception occurred. request_id=%s",
        _request_id(request),
        exc_info=exc,
    )

    return _error_response(
        request=request,
        status_code=500,
        error_type="InternalServerError",
        message="An unexpected error occurred.",
    )
