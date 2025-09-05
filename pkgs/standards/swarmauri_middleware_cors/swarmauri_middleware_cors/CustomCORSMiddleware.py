import logging
from typing import Any, Callable, List

from fastapi import Request, Response
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "CacheControlMiddleware")
class CustomCORSMiddleware(MiddlewareBase):
    """Custom CORS Middleware implementation.

    This middleware provides custom CORS handling for incoming requests.
    It allows for flexible configuration of CORS policies while maintaining
    the core functionality required for secure CORS handling.

    Attributes:
        allow_origins: List[str] = ["*"]  # Allowed origins
        allow_credentials: bool = True    # Whether to allow credentials
        allow_methods: List[str] = ["*"]  # Allowed HTTP methods
        allow_headers: List[str] = ["*"]  # Allowed request headers
        expose_headers: List[str] = []     # Headers to expose in responses
        max_age: int = 600               # Maximum age for CORS configuration
    """

    allow_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    expose_headers: List[str] = []
    max_age: int = 600

    def __init__(
        self,
        allow_origins: List[str] = ["*"],
        allow_credentials: bool = True,
        allow_methods: List[str] = ["*"],
        allow_headers: List[str] = ["*"],
        expose_headers: List[str] = [],
        max_age: int = 600,
        **kwargs: Any,
    ):
        """Initialize the CustomCORSMiddleware with CORS configuration.

        Args:
            allow_origins: List of allowed origins. Defaults to ["*"].
            allow_credentials: Whether to allow credentials. Defaults to True.
            allow_methods: List of allowed HTTP methods. Defaults to ["*"].
            allow_headers: List of allowed request headers. Defaults to ["*"].
            expose_headers: List of headers to expose in responses. Defaults to [].
            max_age: Maximum age for CORS configuration. Defaults to 600.
        """
        super().__init__(**kwargs)
        self.allow_origins = allow_origins
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.expose_headers = expose_headers
        self.max_age = max_age

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatch the request to the next middleware in the chain.

        This method processes the incoming request, performs CORS checks,
        and either allows or denies the request based on the configured
        CORS policy. It then calls the next middleware in the chain.

        Args:
            request: The incoming request object.
            call_next: A callable that invokes the next middleware.

        Returns:
            The response object after processing by all middlewares.
        """
        try:
            if await self.is_options_request(request):
                return await self.handle_options_request(request)

            origin = request.headers.get("Origin", "")
            if not await self.check_cors_origin(origin):
                return self.get_cors_error_response("Invalid origin")

            response = await call_next(request)
            response = await self.add_cors_headers(response)
            return response

        except Exception as e:
            logger.error(f"CORS middleware error: {str(e)}")
            return self.get_cors_error_response("Internal server error")

    async def is_options_request(self, request: Request) -> bool:
        """Check if the request is an OPTIONS request.

        Args:
            request: The incoming request object.

        Returns:
            True if the request method is OPTIONS, False otherwise.
        """
        return request.method == "OPTIONS"

    async def check_cors_origin(self, origin: str) -> bool:
        """Check if the request origin is allowed.

        Args:
            origin: The request origin to check.

        Returns:
            True if the origin is allowed, False otherwise.
        """
        if not origin:
            return False
        if origin in self.allow_origins:
            return True
        return False

    async def handle_options_request(self, request: Request) -> Response:
        """Handle an OPTIONS request.

        This method sets the appropriate CORS headers for OPTIONS requests
        and returns an empty response with status code 200.

        Args:
            request: The incoming OPTIONS request.

        Returns:
            A response object with CORS headers.
        """
        response = Response()
        response = await self.add_cors_headers(response)
        return response

    async def add_cors_headers(self, response: Response) -> Response:
        """Add CORS headers to the response.

        This method adds the configured CORS headers to the response
        object and returns the modified response.

        Args:
            response: The response object to modify.

        Returns:
            The response object with CORS headers added.
        """
        response.headers["Access-Control-Allow-Origin"] = ",".join(self.allow_origins)
        response.headers["Access-Control-Allow-Methods"] = ",".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ",".join(self.allow_headers)
        response.headers["Access-Control-Expose-Headers"] = ",".join(
            self.expose_headers
        )
        response.headers["Access-Control-Allow-Credentials"] = str(
            self.allow_credentials
        ).lower()
        response.headers["Access-Control-Max-Age"] = str(self.max_age)
        return response

    def get_cors_error_response(self, message: str) -> Response:
        """Generate a CORS error response.

        Args:
            message: The error message to include in the response.

        Returns:
            A response object with the error message and appropriate status code.
        """
        response = Response(content=message, status_code=403)
        return response
