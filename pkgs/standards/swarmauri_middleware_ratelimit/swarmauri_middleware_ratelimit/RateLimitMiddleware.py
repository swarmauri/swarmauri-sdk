import logging
import time
from typing import Any, Callable, Literal, Optional

from fastapi import Request, Response
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

# Configure logging
logger = logging.getLogger(__name__)


# Fix: Correct the registration type
@ComponentBase.register_type(MiddlewareBase, "RateLimitMiddleware")
class RateLimitMiddleware(MiddlewareBase, ComponentBase):
    """Enforce per-client request limits.

    The middleware counts requests from each client IP or token within a
    configurable time window. Requests beyond the configured limit are blocked
    with an HTTP ``429`` response.

    Attributes
    ----------
    type : Literal["RateLimitMiddleware"]
        Unique middleware type identifier.
    rate_limit : int, optional
        Maximum number of requests allowed within the time window. Defaults to
        ``100``.
    time_window : int, optional
        Time window in seconds during which the rate limit applies. Defaults to
        ``60`` seconds.
    use_token : bool, optional
        If ``True``, use a token from ``token_header`` instead of the client IP to
        identify callers. Defaults to ``False``.
    token_header : str, optional
        Header name used to extract the token when ``use_token`` is ``True``.
        Defaults to ``"X-Api-Key"``.
    """

    # Fix: Add the type attribute
    type: Literal["RateLimitMiddleware"] = "RateLimitMiddleware"
    rate_limit: Optional[int] = 100
    time_window: Optional[int] = 60
    use_token: Optional[bool] = False
    token_header: Optional[str] = "X-Api-Key"
    _ip_limits: Optional[dict] = {}

    def __init__(
        self,
        rate_limit: int = 100,
        time_window: int = 60,
        use_token: bool = False,
        token_header: str = "X-Api-Key",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.use_token = use_token
        self.token_header = token_header
        self._ip_limits = {}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Process the request while applying rate limits.

        Parameters
        ----------
        request : Request
            Incoming request object.
        call_next : Callable[[Request], Any]
            Callable that invokes the next middleware in the chain.

        Returns
        -------
        Any
            Response object after processing the request.

        Raises
        ------
        HTTPException
            If the client has exceeded the rate limit.
        """

        # Get client identifier (IP or token)
        client_identifier = await self._get_client_identifier(request)

        # Get current timestamp
        current_time = time.time()

        # Initialize or update the client's request count
        if client_identifier not in self._ip_limits:
            self._ip_limits[client_identifier] = {
                "count": 1,
                "last_reset": current_time,
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
        if self._ip_limits[client_identifier]["count"] > self.rate_limit:
            logger.warning(f"Rate limit exceeded for client {client_identifier}")
            return Response(status_code=429, content="Rate limit exceeded")

        # Proceed with the request chain
        return await call_next(request)

    async def _get_client_identifier(self, request: Request) -> str:
        """Return the identifier used for rate limiting.

        If token-based rate limiting is enabled, the token is read from the
        configured header. Otherwise the client's IP address is used.

        Parameters
        ----------
        request : Request
            Incoming request object.

        Returns
        -------
        str
            Client identifier (IP address or token).
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
