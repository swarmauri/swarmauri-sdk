"""JWT Best Current Practices utilities for RFC 8725 compliance.

This module validates JSON Web Tokens according to :rfc:`8725`.  Validation
may be toggled via ``enable_rfc8725`` in
:mod:`auto_authn.runtime_cfg.Settings` to allow deployments to opt in or out
of enforcement.
"""

from __future__ import annotations

from typing import Any, Dict
import base64
import json

from .errors import InvalidTokenError as BaseInvalidTokenError

from .jwtoken import JWTCoder
from .runtime_cfg import settings


class InvalidTokenError(BaseInvalidTokenError):
    """Raised when a JWT violates RFC 8725 recommendations."""


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

    head_b64 = token.split(".")[0]
    pad = "=" * ((4 - (len(head_b64) % 4)) % 4)
    header = json.loads(base64.urlsafe_b64decode(head_b64 + pad))
    if header.get("alg", "").lower() == "none":
        raise InvalidTokenError("alg 'none' is prohibited by RFC 8725")

    for required in ("iss", "aud", "exp", "sub"):
        if required not in claims:
            raise InvalidTokenError(f"missing '{required}' claim required by RFC 8725")

    return claims


__all__ = ["validate_jwt_best_practices", "RFC8725_SPEC_URL"]
