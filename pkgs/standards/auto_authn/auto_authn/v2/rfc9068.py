"""Helpers for the JWT access token profile (RFC 9068).

This module validates that JSON Web Tokens used as OAuth 2.0 access tokens
comply with :rfc:`9068` by checking mandatory claims and the JOSE header
``typ`` value. The feature can be toggled via the runtime settings.
"""

from __future__ import annotations

from typing import Any, Dict

from jwt.exceptions import InvalidTokenError

_REQUIRED_CLAIMS = {"iss", "sub", "aud", "exp", "iat"}


def validate_jwt_access_token(header: Dict[str, Any], payload: Dict[str, Any]) -> None:
    """Validate *header* and *payload* according to RFC 9068.

    Raises ``InvalidTokenError`` if the token does not meet the profile's
    requirements.
    """
    if header.get("typ") != "at+jwt":
        raise InvalidTokenError("typ header must be 'at+jwt' per RFC 9068")
    missing = _REQUIRED_CLAIMS - payload.keys()
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise InvalidTokenError(f"missing required claims per RFC 9068: {missing_list}")


__all__ = ["validate_jwt_access_token"]
