"""Tests for RFC 7515: JSON Web Signature (JWS)."""

from jwcrypto import jwk

from auto_authn.v2 import sign_jws, verify_jws


def test_sign_and_verify_jws() -> None:
    key = jwk.JWK.generate(kty="oct", size=256)
    payload = "payload"
    token = sign_jws(payload, key)
    assert verify_jws(token, key) == payload
