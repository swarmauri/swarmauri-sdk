"""Tests for RFC 7515: JSON Web Signature (JWS)."""

import base64
import secrets

from auto_authn.v2 import sign_jws, verify_jws


def test_sign_and_verify_jws() -> None:
    secret = secrets.token_bytes(32)
    key = {
        "kty": "oct",
        "kind": "raw",
        "key": secret,
        "k": base64.urlsafe_b64encode(secret).rstrip(b"=").decode(),
    }
    payload = "payload"
    token = sign_jws(payload, key)
    assert verify_jws(token, key) == payload
