"""
AuthMiddleware implementation for handling request authentication.
"""

import logging
from typing import Any, Callable

from fastapi import HTTPException, Request
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "AuthMiddleware")
class AuthMiddleware(MiddlewareBase):
    """Middleware for handling request authentication.

    This middleware checks for valid authentication headers or tokens
    in incoming requests and validates them before allowing the request
    to proceed through the application stack.

    Attributes:
        resource: Optional[str] = "auth_middleware"  # Resource type identifier
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatches the request to the next middleware in the chain after authentication.

        This method checks for the presence of a valid authentication token
        in the request headers. If the token is missing or invalid,
        it raises an HTTPException with a 401 status code.

        Args:
            request: The incoming request object to be processed.
            call_next: A callable that invokes the next middleware
                in the chain.

        Returns:
            The response object after all middlewares have processed
            the request.

        Raises:
            HTTPException: If authentication fails.
        """

        # Get the authorization header from the request
        auth_header = request.headers.get("Authorization")

        # Check if the authorization header is missing
        if not auth_header:
            logger.warning("Missing Authorization header in request")
            raise HTTPException(status_code=401, detail="Missing Authorization Header")

        # Check if the header format is correct
        if not auth_header.startswith("Bearer "):
            logger.warning("Invalid Authorization header format")
            raise HTTPException(status_code=401, detail="Invalid token format")

        # Extract the token from the header
        token = auth_header.split("Bearer ")[1]

        # Validate the token (Replace this with actual token validation logic)
        if not token or token != "fake-token":  # Replace with actual validation
            logger.warning("Invalid authentication token")
            raise HTTPException(status_code=401, detail="Invalid token")

        logger.info("Authentication successful")
        return await call_next(request)
