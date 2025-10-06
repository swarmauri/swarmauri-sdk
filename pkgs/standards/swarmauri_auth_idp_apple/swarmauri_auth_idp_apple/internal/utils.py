"""Utility helpers supporting Apple identity provider integrations."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict, Tuple


def _b64u(data: bytes) -> str:
    """Return a URL-safe base64 encoding without padding."""

    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def make_pkce_pair() -> Tuple[str, str]:
    """Generate a PKCE verifier/challenge pair."""

    verifier = _b64u(secrets.token_bytes(32))
    challenge = _b64u(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


def make_nonce() -> str:
    """Generate a cryptographically random nonce."""

    return _b64u(secrets.token_bytes(16))


def sign_state(secret: bytes, payload: Dict[str, Any], ttl_sec: int = 600) -> str:
    """Sign and encode state to protect PKCE and nonce parameters."""

    body = _b64u(
        json.dumps({**payload, "exp": int(time.time()) + ttl_sec}).encode("utf-8")
    )
    digest = hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest()
    mac = _b64u(digest)
    return f"{body}.{mac}"


def verify_state(secret: bytes, state: str) -> Dict[str, Any]:
    """Validate a signed state blob and return the decoded payload."""

    try:
        body, mac = state.split(".", 1)
    except ValueError as exc:  # pragma: no cover - defensive path
        raise ValueError("invalid state format") from exc
    expected = _b64u(hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(mac, expected):
        raise ValueError("bad-mac")
    payload = json.loads(base64.urlsafe_b64decode(body + "=="))
    if payload.get("exp", 0) < time.time():
        raise ValueError("expired")
    return payload
