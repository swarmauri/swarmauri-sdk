from fastapi import FastAPI, Request, Response
from fastapi.middleware import Middleware
from typing import Callable, Any
import time
import logging
from swarmauri_base.middlewares import MiddlewareBase

# Configure logging
logger = logging.getLogger(__name__)

class RateLimitMiddleware(MiddlewareBase):
    """Middleware to enforce rate limits on incoming requests.

    This middleware tracks the number of requests made by each client IP or token
    within a given time window and blocks clients that exceed the specified rate limit.

    Attributes:
        rate_limit (int): Maximum number of requests allowed within the time window.
        time_window (int): Time window in seconds during which the rate limit applies.
        use_token (bool): Whether to use tokens instead of client IP for rate limiting.
        token_header (str): Header name to extract the token from.
    """

    def __init__(self, rate_limit: int = 100, time_window: int = 60, use_token: bool = False, token_header: str = "X-Api-Key"):
        super().__init__()
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.use_token = use_token
        self.token_header = token_header
        self._ip_limits = {}  # Maps client identifiers to their request count and last reset time

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Dispatches the request to the next middleware in the chain while enforcing rate limits.

        Args:
            request: The incoming request object to be processed.
            call_next: A callable that invokes the next middleware in the chain.

        Returns:
            The response object after processing the request.

        Raises:
            HTTPException: If the client has exceeded the rate limit.
        """

        # Get client identifier (IP or token)
        client_identifier = await self._get_client_identifier(request)

        # Get current timestamp
        current_time = time.time()

        # Initialize or update the client's request count
        if client_identifier not in self._ip_limits:
            self._ip_limits[client_identifier] = {
                "count": 1,
                "last_reset": current_time
            }
        else:
            client_data = self._ip_limits[client_identifier]
            # Check if we need to reset the count (time window exceeded)
            if current_time - client_data["last_reset"] > self.time_window:
                client_data["count"] = 1
                client_data["last_reset"] = current_time
            else:
                client_data["count"] += 1

        # Check if the rate limit has been exceeded
        if client_data["count"] > self.rate_limit:
            logger.warning(f"Rate limit exceeded for client {client_identifier}")
            return Response(status_code=429)

        # Proceed with the request chain
        return await call_next(request)

    async def _get_client_identifier(self, request: Request) -> str:
        """Gets the client identifier for rate limiting.

        If token-based rate limiting is enabled, this method retrieves the token
        from the specified header. Otherwise, it returns the client's IP address.

        Args:
            request: The incoming request object.

        Returns:
            str: The client identifier (IP address or token).
        """
        if self.use_token:
            token = request.headers.get(self.token_header)
            if not token:
                raise ValueError(f"Token not found in header {self.token_header}")
            return token
        else:
            # Get client IP, handling proxy cases
            client_ip = request.client.host
            return client_ip