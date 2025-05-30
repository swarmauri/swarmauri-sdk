import logging
import time
from typing import Any, Callable

from fastapi import Request
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "LoggingMiddleware")
class LoggingMiddleware(MiddlewareBase, ComponentBase):
    """Middleware for logging incoming requests and responses.

    This middleware captures and logs important information about incoming
    requests and outgoing responses. It provides visibility into the request
    processing pipeline and helps with debugging and monitoring.

    Attributes:
        resource: Optional[str] = "Middleware"  # Default resource type for middlewares
    """

    def __init__(self):
        """Initializes the LoggingMiddleware instance."""
        super().__init__()
        self.logger = logger

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatches the request to the next middleware in the chain while logging activity.

        This method processes the incoming request, logs relevant information,
        and then passes the request to the next middleware in the chain.

        Args:
            request: The incoming request object to be processed.
            call_next: A callable that invokes the next middleware
                in the chain.

        Returns:
            The response object after all middlewares have processed
            the request.
        """
        # Log incoming request details
        self.logger.info(f"Incoming request: {request.method} {request.url.path}")
        self.logger.info(f"Request headers: {dict(request.headers)}")

        try:
            # Attempt to get request body if available
            request_body = await request.json()
            self.logger.info(f"Request body: {request_body}")
        except Exception as e:
            self.logger.warning(f"Error parsing request body: {str(e)}")

        # Measure request processing time
        start_time = time.time()

        # Process the request with the next middleware
        response = await call_next(request)

        # Log response details
        self.logger.info(f"Response status code: {response.status_code}")
        self.logger.info(
            f"Request completed in: {time.time() - start_time:.4f} seconds"
        )

        return response
