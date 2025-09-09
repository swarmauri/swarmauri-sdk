"""Tests for RFC 7516: JSON Web Encryption (JWE)."""

import asyncio
from secrets import token_bytes

from tigrbl_auth import decrypt_jwe, encrypt_jwe


def test_encrypt_and_decrypt_jwe() -> None:
    key = {"kty": "oct", "k": token_bytes(32)}
    secret = "sensitive"
    token = asyncio.run(encrypt_jwe(secret, key))
    assert asyncio.run(decrypt_jwe(token, key)) == secret
