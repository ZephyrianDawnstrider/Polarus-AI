from collections.abc import Awaitable, Callable
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to each request and response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id: str = str(uuid4())
        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
