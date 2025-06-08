import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware import Middleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(Middleware):
    """Middleware that adds secure HTTP headers to responses.

    This middleware adds various security headers to responses to help
    protect against common web vulnerabilities. The headers implemented
    include Content-Security-Policy, X-Content-Type-Options,
    X-Frame-Options, X-XSS-Protection, Strict-Transport-Security,
    Referrer-Policy, and Permissions-Policy.

    Attributes:
        app: The ASGI application instance
    """

    def __init__(
        self, app: Callable[[Request, Callable[[Request], Response]], Response]
    ):
        super().__init__(app)
        self.app = app

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """Dispatches the request and adds security headers to the response.

        This method is responsible for adding security headers to the response
        before sending it back to the client. It does this by calling the
        next middleware in the chain and then modifying the response
        headers.

        Args:
            request: The incoming request object
            call_next: A callable that invokes the next middleware
                in the chain

        Returns:
            The response object with added security headers
        """
        response = await call_next(request)

        if isinstance(response, Response):
            # Add security headers
            self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response) -> None:
        """Adds security headers to the response.

        This method adds various security headers to the response to
        help protect against common web vulnerabilities.
        """
        logger.info("Adding security headers to response")

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.example.com; "
            "style-src 'self' https://cdn.example.com; "
            "img-src 'self' https://images.example.com; "
            "font-src 'self' https://fonts.example.com"
        )

        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict-Transport-Security
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Referrer-Policy
        response.headers["Referrer-Policy"] = "same-origin"

        # Permissions-Policy
        response.headers["Permissions-Policy"] = (
            "interest-cohort=(), "
            "geolocation=(self), "
            "microphone=(), "
            "camera=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=(self), "
            "vibrate=(), "
            "payment=()"
        )

        logger.info("Successfully added security headers to response")
