"""RFC 7516 - JSON Web Encryption (JWE) helpers via swarmauri plugins."""

from __future__ import annotations

import asyncio
from typing import Any, Final, Mapping

from .deps import JWAAlg, JweCrypto

from .runtime_cfg import settings

RFC7516_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7516"
_crypto = JweCrypto()


def encrypt_jwe(plaintext: str, key: Mapping[str, Any]) -> str:
    """Encrypt *plaintext* for *key* and return the compact JWE string."""
    if not settings.enable_rfc7516:
        raise RuntimeError(f"RFC 7516 support disabled: {RFC7516_SPEC_URL}")
    return asyncio.run(
        _crypto.encrypt_compact(
            payload=plaintext,
            alg=JWAAlg.DIR,
            enc=JWAAlg.A256GCM,
            key=key,
        )
    )


def decrypt_jwe(token: str, key: Mapping[str, Any]) -> str:
    """Decrypt *token* with *key* and return the plaintext string."""
    if not settings.enable_rfc7516:
        raise RuntimeError(f"RFC 7516 support disabled: {RFC7516_SPEC_URL}")
    res = asyncio.run(_crypto.decrypt_compact(token, dir_key=key.get("k")))
    return res.plaintext.decode()


__all__ = ["encrypt_jwe", "decrypt_jwe", "RFC7516_SPEC_URL"]
