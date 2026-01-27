"""Utility helpers shared across auth identity provider implementations."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict, Tuple


def base64url_encode(data: bytes) -> str:
    """Encode bytes using URL-safe base64 without padding."""

    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def make_pkce_pair() -> Tuple[str, str]:
    """Generate a PKCE verifier/challenge pair."""

    verifier = base64url_encode(secrets.token_bytes(32))
    challenge = base64url_encode(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


def sign_state(secret: bytes, payload: Dict[str, Any], ttl_sec: int = 600) -> str:
    """Sign and encode state to protect nonces and PKCE verifiers."""

    body = base64url_encode(
        json.dumps({**payload, "exp": int(time.time()) + ttl_sec}).encode("utf-8")
    )
    digest = hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest()
    mac = base64url_encode(digest)
    return f"{body}.{mac}"


def verify_state(secret: bytes, state: str) -> Dict[str, Any]:
    """Validate a signed state blob and return its decoded payload."""

    try:
        body, mac = state.split(".", 1)
    except ValueError as exc:  # pragma: no cover - defensive path
        raise ValueError("invalid state format") from exc
    expected = base64url_encode(
        hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(mac, expected):
        raise ValueError("bad-mac")
    payload = json.loads(base64.urlsafe_b64decode(body + "=="))
    if payload.get("exp", 0) < time.time():
        raise ValueError("expired")
    return payload


def make_nonce() -> str:
    """Generate a cryptographically random nonce."""

    return base64url_encode(secrets.token_bytes(16))


__all__ = [
    "base64url_encode",
    "make_pkce_pair",
    "sign_state",
    "verify_state",
    "make_nonce",
]
