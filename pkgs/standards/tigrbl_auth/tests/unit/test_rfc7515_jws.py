"""Tests for RFC 7515: JSON Web Signature (JWS)."""

import base64
import secrets
import asyncio

from tigrbl_auth import sign_jws, verify_jws


def test_sign_and_verify_jws() -> None:
    secret = secrets.token_bytes(32)
    key = {
        "kty": "oct",
        "kind": "raw",
        "key": secret,
        "k": base64.urlsafe_b64encode(secret).rstrip(b"=").decode(),
    }
    payload = "payload"
    token = asyncio.run(sign_jws(payload, key))
    assert asyncio.run(verify_jws(token, key)) == payload
