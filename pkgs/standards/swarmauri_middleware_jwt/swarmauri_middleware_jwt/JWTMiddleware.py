"""JWTMiddleware implementation for validating JWT tokens in FastAPI requests."""

import logging
from typing import Any, Callable, Dict, Optional

import jwt
from fastapi import HTTPException, Request
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "JWTMiddleware")
class JWTMiddleware(MiddlewareBase, ComponentBase):
    """Middleware for verifying JWT tokens.

    This middleware validates JWT tokens found in the ``Authorization`` header
    of incoming requests. On successful validation the decoded payload is stored
    on ``request.state.jwt_payload``.

    Attributes:
        secret_key: Secret key used to decode the token.
        algorithm: Algorithm used for decoding (default ``HS256``).
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256", **kwargs: Any) -> None:
        """Initialize JWTMiddleware with token settings."""
        super().__init__(**kwargs)
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Validate the JWT token and continue processing."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header")
            raise HTTPException(status_code=401, detail="Invalid authorization token")

        token = auth_header.split("Bearer ", 1)[1].strip()
        try:
            payload = self.verify_token(token)
        except jwt.PyJWTError as exc:
            logger.error(f"Token validation failed: {exc}")
            raise HTTPException(status_code=401, detail="Invalid token") from exc

        request.state.jwt_payload = payload
        return await call_next(request)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Decode a JWT token using the configured secret key."""
        return jwt.decode(token, key=self.secret_key, algorithms=[self.algorithm])
