"""Tests for RFC 7520: JOSE Examples."""

from jwcrypto import jwk

from auto_authn.v2 import jws_then_jwe, jwe_then_jws


def test_jws_then_jwe_roundtrip() -> None:
    key = jwk.JWK.generate(kty="oct", size=256)
    message = "hello"
    token = jws_then_jwe(message, key)
    assert jwe_then_jws(token, key) == message
