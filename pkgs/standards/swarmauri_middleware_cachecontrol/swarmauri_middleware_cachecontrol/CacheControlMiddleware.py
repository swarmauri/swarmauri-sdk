import logging
from datetime import datetime
from typing import Any, Callable

from fastapi import Request, Response
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "CacheControlMiddleware")
class CacheControlMiddleware(MiddlewareBase, ComponentBase):
    """Middleware for managing HTTP cache headers and client-side caching behavior.

    This middleware controls how responses are cached by clients and proxies.
    It sets appropriate Cache-Control headers and handles conditional requests.

    Attributes:
        max_age: int = 3600  # Maximum age (in seconds) for caching
        enabled: bool = True   # Whether caching is enabled
    """

    max_age: int = 3600
    enabled: bool = True

    def __init__(
        self, max_age: int = 3600, enabled: bool = True, **kwargs: Any
    ) -> None:
        """Initialize the CacheControlMiddleware instance."""
        super().__init__(**kwargs)
        self.max_age = max_age
        self.enabled = enabled

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatch the request and control caching behavior.

        This method processes the request, sets appropriate caching headers,
        and handles conditional requests based on client headers.

        Args:
            request: The incoming FastAPI request object
            call_next: Callable that calls the next middleware or route handler

        Returns:
            The response object with caching headers set
        """

        response = await call_next(request)

        if not isinstance(response, Response):
            return response

        if not self.enabled:
            return response

        # Set Cache-Control header
        self._set_cache_control_headers(response)

        # Handle conditional requests
        if await self._handle_conditional_request(request, response):
            return response

        return response

    def _set_cache_control_headers(self, response: Response):
        """Set appropriate caching headers on the response."""
        cache_control = f"max-age={self.max_age}, public"
        response.headers["Cache-Control"] = cache_control

        # Set ETag based on current timestamp
        etag = f'"{datetime.now().timestamp()}"'
        response.headers["ETag"] = etag

        # Add Vary header to indicate caching behavior
        response.headers["Vary"] = "Accept-Encoding"

    async def _handle_conditional_request(
        self, request: Request, response: Response
    ) -> bool:
        """Check for conditional request headers and handle accordingly."""
        if_modified_since = request.headers.get("If-Modified-Since")
        if_none_match = request.headers.get("If-None-Match")

        current_time = datetime.now()
        current_timestamp = current_time.timestamp()

        # Handle If-Modified-Since
        if if_modified_since:
            modified_since = datetime.strptime(
                if_modified_since, "%a, %d %b %Y %H:%M:%S %Z"
            ).timestamp()

            if current_timestamp <= modified_since:
                return await self._send_not_modified(response)

        # Handle If-None-Match
        if if_none_match:
            current_etag = response.headers.get("ETag", "")
            if if_none_match.strip('"') == current_etag.strip('"'):
                return await self._send_not_modified(response)

        return False

    async def _send_not_modified(self, response: Response) -> bool:
        """Send a 304 Not Modified response."""
        response.status_code = 304
        response.body = b""
        # Fix: Use del instead of pop() for MutableHeaders
        if "Content-Length" in response.headers:
            del response.headers["Content-Length"]

        # Set cache control headers
        response.headers["Cache-Control"] = f"max-age={self.max_age}, public"
        response.headers["ETag"] = response.headers.get("ETag", "")
        response.headers["Vary"] = "Accept-Encoding"

        logger.info("Sent 304 Not Modified response")
        return True
