"""RFC 7516 - JSON Web Encryption (JWE).

Helpers for encrypting and decrypting content using the compact JWE
serialization. This feature can be toggled with the
``AUTO_AUTHN_ENABLE_RFC7516`` environment variable.

See RFC 7516: https://www.rfc-editor.org/rfc/rfc7516
"""

from typing import Final

from jwcrypto import jwe, jwk

from .runtime_cfg import settings

RFC7516_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7516"


def encrypt_jwe(plaintext: str, key: jwk.JWK) -> str:
    """Encrypt *plaintext* for *key* and return the compact JWE string."""
    if not settings.enable_rfc7516:
        raise RuntimeError(f"RFC 7516 support disabled: {RFC7516_SPEC_URL}")
    protected = {"alg": "dir", "enc": "A256GCM"}
    token = jwe.JWE(plaintext.encode(), json_encode(protected))
    token.add_recipient(key)
    return token.serialize()


def decrypt_jwe(token: str, key: jwk.JWK) -> str:
    """Decrypt *token* with *key* and return the plaintext string."""
    if not settings.enable_rfc7516:
        raise RuntimeError(f"RFC 7516 support disabled: {RFC7516_SPEC_URL}")
    obj = jwe.JWE()
    obj.deserialize(token)
    obj.decrypt(key)
    return obj.payload.decode()


def json_encode(data: dict) -> str:
    import json

    return json.dumps(data)


__all__ = ["encrypt_jwe", "decrypt_jwe", "RFC7516_SPEC_URL"]
