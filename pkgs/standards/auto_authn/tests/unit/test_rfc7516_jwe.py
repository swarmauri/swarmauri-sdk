"""Tests for RFC 7516: JSON Web Encryption (JWE)."""

from jwcrypto import jwk

from auto_authn.v2 import encrypt_jwe, decrypt_jwe


def test_encrypt_and_decrypt_jwe() -> None:
    key = jwk.JWK.generate(kty="oct", size=256)
    secret = "sensitive"
    token = encrypt_jwe(secret, key)
    assert decrypt_jwe(token, key) == secret
