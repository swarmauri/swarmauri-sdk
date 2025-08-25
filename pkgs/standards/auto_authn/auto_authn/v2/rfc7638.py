"""JWK Thumbprint utilities for RFC 7638 compliance.

This module computes and verifies JSON Web Key (JWK) thumbprints as defined in
:rfc:`7638`.  The helpers are feature flagged via ``enable_rfc7638`` in
:mod:`auto_authn.v2.runtime_cfg` so deployments may opt out of enforcement.
"""

from __future__ import annotations

import base64
import json
from hashlib import sha256
from typing import Any, Mapping

from .runtime_cfg import settings

# Required members for each key type according to RFC 7638 §3.1
_REQUIRED_MEMBERS = {
    "RSA": ("e", "kty", "n"),
    "EC": ("crv", "kty", "x", "y"),
    "OKP": ("crv", "kty", "x"),
    "oct": ("k", "kty"),
}


def jwk_thumbprint(jwk: Mapping[str, Any], *, enabled: bool | None = None) -> str:
    """Return the JWK thumbprint for *jwk* per :rfc:`7638`.

    When ``enabled`` is ``False`` the function returns an empty string to allow
    systems to bypass the computation.  If ``enabled`` is ``None`` the global
    ``runtime_cfg.settings.enable_rfc7638`` toggle is consulted.
    """

    if enabled is None:
        enabled = settings.enable_rfc7638
    if not enabled:
        return ""
    kty = jwk.get("kty")
    members = _REQUIRED_MEMBERS.get(kty)
    if not members:
        raise ValueError(f"unsupported kty: {kty}")
    obj = {k: jwk[k] for k in members}
    canonical = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
    digest = sha256(canonical).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def verify_jwk_thumbprint(
    jwk: Mapping[str, Any], thumbprint: str, *, enabled: bool | None = None
) -> bool:
    """Return ``True`` if *thumbprint* matches *jwk* according to :rfc:`7638`.

    The check is controlled by the same feature flag as :func:`jwk_thumbprint`.
    When disabled the function returns ``True`` to allow non-compliant clients.
    """

    if enabled is None:
        enabled = settings.enable_rfc7638
    if not enabled:
        return True
    try:
        expected = jwk_thumbprint(jwk, enabled=True)
    except Exception:
        return False
    return expected == thumbprint


__all__ = ["jwk_thumbprint", "verify_jwk_thumbprint"]
