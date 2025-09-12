"""Utilities for logging HTTP request and response details to stdout."""

import logging
from typing import Any, Callable

from fastapi import Request
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "StdioMiddleware")
class StdioMiddleware(MiddlewareBase):
    """Log request and response details to stdout.

    The middleware writes basic information about each request and the
    corresponding response status to standard output. It is primarily
    intended for development and debugging.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Log the request, call the next handler, then log the response.

        request (Request): Incoming HTTP request.
        call_next (Callable[[Request], Any]): Callable that invokes the next
            middleware or endpoint.
        RETURNS (Any): Response produced by the downstream middleware or
            endpoint.
        """
        logger.info("STDIO Request: %s %s", request.method, request.url.path)
        response = await call_next(request)
        status = getattr(response, "status_code", "unknown")
        logger.info("STDIO Response: %s", status)
        return response
