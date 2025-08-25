"""JWT Best Current Practices utilities for RFC 8725 compliance.

This module validates JSON Web Tokens according to :rfc:`8725`.  Validation
may be toggled via ``enable_rfc8725`` in
:mod:`auto_authn.v2.runtime_cfg.Settings` to allow deployments to opt in or out
of enforcement.
"""

from __future__ import annotations

from typing import Any, Dict

import jwt
from jwt.exceptions import InvalidTokenError

from .jwtoken import JWTCoder
from .runtime_cfg import settings

RFC8725_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8725"


def validate_jwt_best_practices(
    token: str, *, enabled: bool | None = None
) -> Dict[str, Any]:
    """Return decoded *token* if it satisfies :rfc:`8725` recommendations.

    When ``enabled`` is ``False`` the token is decoded without additional
    validation.  If ``enabled`` is ``None`` the global runtime setting is used.
    """

    if enabled is None:
        enabled = settings.enable_rfc8725

    # Always decode using the standard JWTCoder to verify signature and expiry
    claims = JWTCoder.default().decode(token)
    if not enabled:
        return claims

    header = jwt.get_unverified_header(token)
    if header.get("alg", "").lower() == "none":
        raise InvalidTokenError("alg 'none' is prohibited by RFC 8725")

    for required in ("iss", "aud", "exp", "sub"):
        if required not in claims:
            raise InvalidTokenError(f"missing '{required}' claim required by RFC 8725")

    return claims


__all__ = ["validate_jwt_best_practices", "RFC8725_SPEC_URL"]
