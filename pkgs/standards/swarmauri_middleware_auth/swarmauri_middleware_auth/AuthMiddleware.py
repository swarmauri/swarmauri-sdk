"""
AuthMiddleware implementation for handling JWT authentication.
"""

import asyncio
import json
import logging
import time
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_signing_jws import JwsSignerVerifier

logger = logging.getLogger(__name__)


class InvalidTokenError(Exception):
    """Raised when custom JWT validation fails."""

    pass


@ComponentBase.register_type(MiddlewareBase, "AuthMiddleware")
class AuthMiddleware(MiddlewareBase, ComponentBase):
    """Middleware for handling JWT authentication.

    This middleware validates JWT tokens in incoming requests and ensures
    they are properly signed and not expired before allowing the request
    to proceed through the application stack.

    Attributes:
        secret_key: Secret key used to verify JWT tokens
        algorithm: Algorithm used for JWT verification (default: HS256)
        verify_exp: Whether to verify token expiration (default: True)
        verify_aud: Whether to verify audience claim (default: False)
        audience: Expected audience for token verification
        issuer: Expected issuer for token verification
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        verify_exp: bool = True,
        verify_aud: bool = False,
        audience: Optional[str] = None,
        issuer: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize the AuthMiddleware with JWT configuration.

        Args:
            secret_key: Secret key used to verify JWT tokens
            algorithm: Algorithm used for JWT verification
            verify_exp: Whether to verify token expiration
            verify_aud: Whether to verify audience claim
            audience: Expected audience for token verification
            issuer: Expected issuer for token verification
        """
        super().__init__(**kwargs)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.verify_exp = verify_exp
        self.verify_aud = verify_aud
        self.audience = audience
        self.issuer = issuer
        self._jws = JwsSignerVerifier()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatches the request after JWT authentication.

        This method extracts and validates JWT tokens from the Authorization header.
        It checks for proper format, signature, expiration, and other claims
        as configured.

        Args:
            request: The incoming request object to be processed.
            call_next: A callable that invokes the next middleware in the chain.

        Returns:
            The response object after all middlewares have processed the request.

        Raises:
            HTTPException: If authentication fails for any reason.
        """

        # Get the authorization header from the request
        auth_header = request.headers.get("Authorization")

        # Check if the authorization header is missing
        if not auth_header:
            logger.warning("Missing Authorization header in request")
            raise HTTPException(status_code=401, detail="Missing Authorization header")

            # Check if the header format is correct
        if not auth_header.startswith("Bearer "):
            logger.warning("Invalid Authorization header format")
            raise HTTPException(status_code=401, detail="Invalid token format")

            # Extract the token from the header
        try:
            token = auth_header.split("Bearer ")[1].strip()
            if not token:
                raise ValueError("Empty token")
        except (IndexError, ValueError):
            logger.warning("Failed to extract token from Authorization header")
            raise HTTPException(status_code=401, detail="Invalid token format")

            # Validate the JWT token
        try:
            payload = await self._validate_jwt_token(token)

            # Add the decoded payload to request state for use in downstream handlers
            request.state.user = payload

            logger.info(
                f"Authentication successful for user: {payload.get('sub', 'unknown')}"
            )
            return await call_next(request)

        except HTTPException as exc:
            logger.warning(exc.detail)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during JWT validation: {str(e)}")
            raise HTTPException(status_code=401, detail="Authentication failed")

    async def _validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return its payload."""

        try:
            res = await self._jws.verify_compact(
                token,
                hmac_keys=[
                    {"kind": "raw", "key": self.secret_key, "alg": self.algorithm}
                ],
                alg_allowlist=[JWAAlg(self.algorithm)],
            )
        except Exception as e:
            logger.debug(f"JWT signature verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid token signature")

        payload = json.loads(res.payload.decode("utf-8"))
        now = int(time.time())
        if self.verify_exp:
            exp = payload.get("exp")
            if exp is None or now > int(exp):
                raise HTTPException(status_code=401, detail="Token has expired")
        if self.verify_aud and self.audience:
            if payload.get("aud") != self.audience:
                raise HTTPException(status_code=401, detail="Invalid token audience")
        if self.issuer and payload.get("iss") != self.issuer:
            raise HTTPException(status_code=401, detail="Invalid token issuer")

        # Additional custom validations can be added here
        self._validate_custom_claims(payload)
        return payload

    def _validate_custom_claims(self, payload: Dict[str, Any]) -> None:
        """Validate custom claims in the JWT payload.

        This method can be overridden to implement custom validation logic
        for specific claims in your JWT tokens.

        Args:
            payload: The decoded JWT payload

        Raises:
            InvalidTokenError: If custom validation fails
        """

        # Example: Validate required claims
        required_claims = ["sub", "iat"]
        for claim in required_claims:
            if claim not in payload:
                raise InvalidTokenError(f"Missing required claim: {claim}")

    def verify_token_manually(self, token: str) -> Optional[Dict[str, Any]]:
        """Manually verify a token without raising exceptions.

        This is a utility method that can be used for token verification
        outside of the middleware context.

        Args:
            token: The JWT token string to verify

        Returns:
            Dict containing the decoded payload if valid, None if invalid
        """
        try:
            return asyncio.run(self._validate_jwt_token(token))
        except Exception as e:
            logger.debug(f"Token verification failed: {str(e)}")
            return None
