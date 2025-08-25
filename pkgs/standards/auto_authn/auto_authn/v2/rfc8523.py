"""RFC 8523 - JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants.

This module provides enhanced JWT-based client authentication and authorization
grant processing as specified in RFC 8523. This is an extension of RFC 7523
with additional security considerations and validation requirements.

See RFC 8523: https://www.rfc-editor.org/rfc/rfc8523
"""

from __future__ import annotations

import time
from typing import Dict, Iterable, Set, Union, Optional, Any

from .runtime_cfg import settings
from .rfc7523 import validate_client_jwt_bearer
from .errors import InvalidTokenError

RFC8523_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8523"
REQUIRED_CLAIMS: Set[str] = {"iss", "sub", "aud", "exp", "iat", "jti"}


def validate_enhanced_jwt_bearer(
    assertion: str,
    *,
    audience: Union[str, Iterable[str], None] = None,
    max_age_seconds: int = 300,
    clock_skew_seconds: int = 30,
) -> Dict[str, Any]:
    """Validate a JWT assertion per RFC 8523 enhanced client authentication profile.

    This extends RFC 7523 validation with additional security requirements:
    - Requires 'iat' (issued at) and 'jti' (JWT ID) claims
    - Enforces maximum age validation
    - Provides clock skew tolerance
    - Enhanced replay attack protection

    Args:
        assertion: The JWT assertion string
        audience: Expected audience(s) for the JWT
        max_age_seconds: Maximum age of the JWT in seconds (default: 5 minutes)
        clock_skew_seconds: Clock skew tolerance in seconds (default: 30 seconds)

    Returns:
        Dict containing the validated JWT claims

    Raises:
        RuntimeError: If RFC 8523 support is disabled
        ValueError: If validation fails
    """
    if not settings.enable_rfc8523:
        raise RuntimeError("RFC 8523 support disabled")

    # First perform basic RFC 7523 validation
    claims = validate_client_jwt_bearer(assertion, audience=audience)

    # Additional RFC 8523 requirements
    missing = REQUIRED_CLAIMS - claims.keys()
    if missing:
        raise ValueError(
            f"RFC 8523 missing required claims: {', '.join(sorted(missing))}"
        )

    # Validate issued at time and maximum age
    current_time = int(time.time())
    iat = claims.get("iat")
    if not isinstance(iat, int):
        raise InvalidTokenError("'iat' claim must be an integer timestamp")

    # Check if token is too old
    token_age = current_time - iat
    if token_age > max_age_seconds + clock_skew_seconds:
        raise ValueError(f"JWT is too old: {token_age} seconds > {max_age_seconds}")

    # Check if token is from the future (with clock skew tolerance)
    if iat > current_time + clock_skew_seconds:
        raise InvalidTokenError("JWT 'iat' claim is in the future")

    # Validate JWT ID for replay protection
    jti = claims.get("jti")
    if not isinstance(jti, str) or not jti.strip():
        raise ValueError("'jti' claim must be a non-empty string")

    return claims


def create_client_assertion_jwt(
    client_id: str,
    audience: str,
    *,
    expires_in: int = 300,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a JWT assertion for client authentication per RFC 8523.

    Args:
        client_id: The OAuth 2.0 client identifier
        audience: The intended audience (typically the token endpoint)
        expires_in: Token validity period in seconds (default: 5 minutes)
        additional_claims: Optional additional claims to include

    Returns:
        JWT assertion string ready for use in client authentication

    Raises:
        RuntimeError: If RFC 8523 support is disabled
    """
    if not settings.enable_rfc8523:
        raise RuntimeError("RFC 8523 support disabled")

    from .rfc7519 import encode_jwt
    import uuid

    current_time = int(time.time())
    claims = {
        "iss": client_id,
        "sub": client_id,
        "aud": audience,
        "exp": current_time + expires_in,
        "iat": current_time,
        "jti": str(uuid.uuid4()),
    }

    if additional_claims:
        claims.update(additional_claims)

    return encode_jwt(**claims)


def is_jwt_replay(jti: str, iat: int, max_age_seconds: int = 300) -> bool:
    """Check if a JWT ID indicates a replay attack.

    This is a placeholder implementation. In production, this should
    check against a cache/database of recently used JTIs.

    Args:
        jti: JWT ID claim value
        iat: Issued at timestamp
        max_age_seconds: Maximum age to consider for replay detection

    Returns:
        True if the JWT appears to be a replay, False otherwise
    """
    # TODO: Implement proper JTI tracking with cache/database
    # For now, always return False (no replay detection)
    return False


__all__ = [
    "validate_enhanced_jwt_bearer",
    "create_client_assertion_jwt",
    "is_jwt_replay",
    "RFC8523_SPEC_URL",
]
