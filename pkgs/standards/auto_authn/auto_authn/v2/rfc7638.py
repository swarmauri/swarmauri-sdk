"""JSON Web Key (JWK) Thumbprint (RFC 7638).

This module provides a helper to compute the JWK thumbprint as defined in
`RFC 7638 <https://datatracker.ietf.org/doc/html/rfc7638>`_. The helper is
feature flagged via ``enable_rfc7638`` in :mod:`auto_authn.v2.runtime_cfg` so
that projects may opt in to this behaviour.
"""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any, Dict

from .runtime_cfg import settings

RFC7638_SPEC_URL = "https://datatracker.ietf.org/doc/html/rfc7638"


def jwk_thumbprint(jwk: Dict[str, Any]) -> str:
    """Return the base64url-encoded SHA-256 JWK thumbprint.

    Raises ``RuntimeError`` if the feature is disabled. Only RSA and EC keys
    are supported for simplicity.
    """
    if not settings.enable_rfc7638:
        raise RuntimeError("RFC 7638 support disabled")
    kty = jwk.get("kty")
    if kty == "RSA":
        members = {k: jwk[k] for k in ("e", "kty", "n")}
    elif kty == "EC":
        members = {k: jwk[k] for k in ("crv", "kty", "x", "y")}
    else:
        raise ValueError("Unsupported key type for thumbprint")
    json_str = json.dumps(members, separators=(",", ":"), sort_keys=True)
    digest = hashlib.sha256(json_str.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


__all__ = ["jwk_thumbprint", "RFC7638_SPEC_URL"]
