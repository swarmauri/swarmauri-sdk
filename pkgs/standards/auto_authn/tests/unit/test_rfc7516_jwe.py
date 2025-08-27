"""Tests for RFC 7516: JSON Web Encryption (JWE)."""

from secrets import token_bytes

from auto_authn import decrypt_jwe, encrypt_jwe


def test_encrypt_and_decrypt_jwe() -> None:
    key = {"kty": "oct", "k": token_bytes(32)}
    secret = "sensitive"
    token = encrypt_jwe(secret, key)
    assert decrypt_jwe(token, key) == secret
