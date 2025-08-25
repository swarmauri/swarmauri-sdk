"""
AuthMiddleware implementation for handling JWT authentication.
"""

import logging
from typing import Any, Callable, Dict, Optional

import jwt
from fastapi import HTTPException, Request
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase
from swarmauri_core.crypto.types import JWAAlg

logger = logging.getLogger(__name__)


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
        algorithm: JWAAlg = JWAAlg.HS256,
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
            payload = self._validate_jwt_token(token)

            # Add the decoded payload to request state for use in downstream handlers
            request.state.user = payload

            logger.info(
                f"Authentication successful for user: {payload.get('sub', 'unknown')}"
            )
            return await call_next(request)

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")

        except jwt.InvalidSignatureError:
            logger.warning("JWT token has invalid signature")
            raise HTTPException(status_code=401, detail="Invalid token signature")

        except jwt.InvalidAudienceError:
            logger.warning("JWT token has invalid audience")
            raise HTTPException(status_code=401, detail="Invalid token audience")

        except jwt.InvalidIssuerError:
            logger.warning("JWT token has invalid issuer")
            raise HTTPException(status_code=401, detail="Invalid token issuer")

        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")

        except Exception as e:
            logger.error(f"Unexpected error during JWT validation: {str(e)}")
            raise HTTPException(status_code=401, detail="Authentication failed")

    def _validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return its payload.

        Args:
            token: The JWT token string to validate

        Returns:
            Dict containing the decoded JWT payload

        Raises:
            jwt.InvalidTokenError: If the token is invalid
            jwt.ExpiredSignatureError: If the token has expired
            jwt.InvalidSignatureError: If the token signature is invalid
            jwt.InvalidAudienceError: If the audience claim is invalid
            jwt.InvalidIssuerError: If the issuer claim is invalid
        """

        # Prepare verification options
        options = {
            "verify_signature": True,
            "verify_exp": self.verify_exp,
            "verify_nbf": True,  # Verify "not before" claim
            "verify_iat": True,  # Verify "issued at" claim
            "verify_aud": self.verify_aud,
            "verify_iss": self.issuer is not None,
        }

        # Prepare decode arguments
        decode_kwargs = {
            "key": self.secret_key,
            "algorithms": [self.algorithm.value],
            "options": options,
        }

        # Add audience if specified
        if self.verify_aud and self.audience:
            decode_kwargs["audience"] = self.audience

        # Add issuer if specified
        if self.issuer:
            decode_kwargs["issuer"] = self.issuer

        # Decode and validate the token
        payload = jwt.decode(token, **decode_kwargs)

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
            jwt.InvalidTokenError: If custom validation fails
        """

        # Example: Validate required claims
        required_claims = ["sub", "iat"]
        for claim in required_claims:
            if claim not in payload:
                raise jwt.InvalidTokenError(f"Missing required claim: {claim}")

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
            return self._validate_jwt_token(token)
        except Exception as e:
            logger.debug(f"Token verification failed: {str(e)}")
            return None
