import logging
from typing import Any, Callable

from fastapi import Request
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "StdioMiddleware")
class StdioMiddleware(MiddlewareBase):
    """Middleware that logs request and response information to stdout."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Log the request, pass it to the next middleware, then log the response."""
        logger.info("STDIO Request: %s %s", request.method, request.url.path)
        response = await call_next(request)
        status = getattr(response, "status_code", "unknown")
        logger.info("STDIO Response: %s", status)
        return response
