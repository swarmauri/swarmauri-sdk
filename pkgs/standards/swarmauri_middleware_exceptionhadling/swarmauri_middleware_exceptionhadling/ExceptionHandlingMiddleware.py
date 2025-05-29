import json
import logging
from datetime import datetime
from typing import Any, Callable

from fastapi import Request, Response
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase
from swarmauri_core.middlewares.IMiddleware import IMiddleware

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "ExceptionHandlingMiddleware")
class ExceptionHandlingMiddleware(MiddlewareBase, IMiddleware):
    """Middleware for handling exceptions and errors across the application."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatches the request to the next middleware in the chain while handling exceptions."""
        try:
            # Call the next middleware in the chain
            return await call_next(request)

        except Exception as e:
            # Log the exception with request details
            logger.error(
                "Unhandled exception occurred while processing request",
                exc_info=True,
                extra={
                    "request_method": request.method,
                    "request_path": request.url.path,
                    "request_headers": dict(request.headers),
                },
            )

            # Prepare the error response
            error_response = {
                "error": {
                    "type": "Unhandled Exception",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat(),  # Fix: Remove duplicate datetime
                }
            }

            # Return a JSON response with 500 status code
            return Response(
                content=json.dumps(error_response),  # Fix: Serialize to JSON string
                status_code=500,
                media_type="application/json",
            )

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        """Makes the middleware callable.

        Args:
            request: The incoming request object.
            call_next: The next middleware/handler in the chain.

        Returns:
            The response object after processing.
        """
        return await self.dispatch(request, call_next)  # Fix: Pass call_next parameter
