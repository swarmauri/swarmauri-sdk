"""RFC 7521 - Assertion Framework for OAuth 2.0.

This module provides helpers for validating JWT assertions used for client
authentication and authorization grants. Support can be toggled via the
``AUTO_AUTHN_ENABLE_RFC7521`` environment variable.

See RFC 7521: https://www.rfc-editor.org/rfc/rfc7521
"""

from __future__ import annotations

from typing import Dict, Set

from .runtime_cfg import settings
from .rfc7519 import decode_jwt

RFC7521_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc7521"
REQUIRED_CLAIMS: Set[str] = {"iss", "sub", "aud", "exp"}


def validate_jwt_assertion(assertion: str) -> Dict[str, object]:
    """Validate a JWT ``assertion`` per RFC 7521.

    The JWT MUST contain the ``iss``, ``sub``, ``aud`` and ``exp`` claims as
    required by RFC 7521 §3. If support for RFC 7521 is disabled, a
    ``RuntimeError`` is raised.
    """

    if not settings.enable_rfc7521:
        raise RuntimeError(f"RFC 7521 support disabled: {RFC7521_SPEC_URL}")
    claims = decode_jwt(assertion)
    missing = REQUIRED_CLAIMS - claims.keys()
    if missing:
        raise ValueError(f"missing claims: {', '.join(sorted(missing))}")
    return claims


__all__ = ["validate_jwt_assertion", "RFC7521_SPEC_URL"]
