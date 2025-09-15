"""RFC 7523 - JSON Web Token (JWT) Profile for OAuth 2.0.

This module provides helpers for validating JWT bearer assertions used for
client authentication and authorization grants.  Support can be toggled via the
``TIGRBL_AUTH_ENABLE_RFC7523`` environment variable.
"""

from __future__ import annotations

from typing import Dict, Iterable, Set, Union

from ..runtime_cfg import settings
from .rfc7519 import decode_jwt

RFC7523_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc7523"
REQUIRED_CLAIMS: Set[str] = {"iss", "sub", "aud", "exp"}


def validate_client_jwt_bearer(
    assertion: str, *, audience: Union[str, Iterable[str], None] = None
) -> Dict[str, object]:
    """Validate a JWT ``assertion`` per RFC 7523 client authentication profile.

    The JWT MUST contain the ``iss``, ``sub``, ``aud`` and ``exp`` claims and the
    ``iss`` and ``sub`` values MUST match as required by RFC 7523 §2.2. If
    support for RFC 7523 is disabled, a ``RuntimeError`` is raised. When
    ``audience`` is provided, the JWT's ``aud`` claim must match one of the
    expected values per RFC 7523 §2.2.
    """

    if not settings.enable_rfc7523:
        raise RuntimeError("RFC 7523 support disabled")
    claims = decode_jwt(assertion)
    missing = REQUIRED_CLAIMS - claims.keys()
    if missing:
        raise ValueError(f"missing claims: {', '.join(sorted(missing))}")
    if claims["iss"] != claims["sub"]:
        raise ValueError("iss and sub must match for client authentication")
    if audience is not None:
        aud_claim = claims["aud"]
        aud_values = {aud_claim} if isinstance(aud_claim, str) else set(aud_claim)
        expected = {audience} if isinstance(audience, str) else set(audience)
        if aud_values.isdisjoint(expected):
            raise ValueError("invalid audience")
    return claims


__all__ = ["validate_client_jwt_bearer", "RFC7523_SPEC_URL"]
