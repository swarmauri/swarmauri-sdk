"""Utilities for OAuth 2.0 Demonstrating Proof of Possession (DPoP).

This module provides helpers to create and verify DPoP proofs as defined in
RFC 9449. It currently supports Ed25519 keys and is intentionally lightweight
so the feature can be enabled or disabled via runtime configuration.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .runtime_cfg import settings

RFC9449_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc9449"

_ALG = "EdDSA"
_ALLOWED_SKEW = 300  # seconds


def _b64url(data: bytes) -> str:
    """Return base64url encoded string without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


# ---------------------------------------------------------------------------
# JWK helpers
# ---------------------------------------------------------------------------


def jwk_from_public_key(public_key: Ed25519PublicKey) -> Dict[str, str]:
    """Return a public JWK for *public_key* (Ed25519 only)."""
    x = _b64url(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )
    return {"kty": "OKP", "crv": "Ed25519", "x": x}


def jwk_thumbprint(jwk: Dict[str, str]) -> str:
    """Compute the RFC 7638 SHA-256 thumbprint for *jwk*."""
    data = json.dumps({k: jwk[k] for k in sorted(jwk)}, separators=(",", ":")).encode()
    digest = hashlib.sha256(data).digest()
    return _b64url(digest)


# ---------------------------------------------------------------------------
# DPoP proof helpers
# ---------------------------------------------------------------------------


def create_proof(
    private_pem: bytes, method: str, url: str, *, enabled: bool | None = None
) -> str:
    """Return a DPoP proof for *method* and *url* signed by *private_pem*.

    When ``enabled`` is ``False`` an empty string is returned to allow callers
    to bypass proof generation.
    """
    if enabled is None:
        enabled = settings.enable_rfc9449
    if not enabled:
        return ""
    private = serialization.load_pem_private_key(private_pem, password=None)
    if not isinstance(private, Ed25519PrivateKey):  # pragma: no cover - sanity
        raise TypeError("Ed25519 key required")
    jwk = jwk_from_public_key(private.public_key())
    headers = {"typ": "dpop+jwt", "alg": _ALG, "jwk": jwk}
    payload = {
        "htm": method.upper(),
        "htu": url,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, private_pem, algorithm=_ALG, headers=headers)


def verify_proof(
    proof: str,
    method: str,
    url: str,
    *,
    jkt: str | None = None,
    enabled: bool | None = None,
) -> str:
    """Verify *proof* for *method*/*url* and optionally enforce *jkt* binding.

    Returns the computed JWK thumbprint if verification succeeds and raises
    ``ValueError`` otherwise. When ``enabled`` is ``False`` an empty string is
    returned without performing any verification.
    """

    if enabled is None:
        enabled = settings.enable_rfc9449
    if not enabled:
        return ""

    try:
        header = jwt.get_unverified_header(proof)
    except jwt.exceptions.DecodeError as exc:  # pragma: no cover - sanity
        raise ValueError("malformed DPoP proof") from exc

    jwk = header.get("jwk")
    if not jwk:
        raise ValueError("missing jwk in DPoP header")
    if jwk.get("kty") != "OKP" or jwk.get("crv") != "Ed25519":
        raise ValueError("unsupported jwk")

    public_key = Ed25519PublicKey.from_public_bytes(
        base64.urlsafe_b64decode(jwk["x"] + "==")
    )
    payload = jwt.decode(proof, public_key, algorithms=[_ALG])

    if payload.get("htm") != method.upper():
        raise ValueError("htm mismatch")
    if payload.get("htu") != url:
        raise ValueError("htu mismatch")

    now = int(time.time())
    iat = int(payload.get("iat", 0))
    if abs(now - iat) > _ALLOWED_SKEW:
        raise ValueError("iat out of range")

    thumb = jwk_thumbprint(jwk, enabled=True)
    if jkt and thumb != jkt:
        raise ValueError("jkt mismatch")
    return thumb


__all__ = [
    "RFC9449_SPEC_URL",
    "create_proof",
    "verify_proof",
    "jwk_from_public_key",
    "jwk_thumbprint",
]
