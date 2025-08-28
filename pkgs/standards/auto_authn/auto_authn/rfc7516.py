"""RFC 7516 - JSON Web Encryption (JWE) helpers via swarmauri plugins."""

from __future__ import annotations

import base64
from typing import Any, Final, Mapping

from .deps import JWAAlg, JweCrypto

from .runtime_cfg import settings

RFC7516_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7516"
_crypto = JweCrypto()


def _normalize_oct_key(key: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return *key* with its ``"k"`` decoded from base64url if needed."""
    k = key.get("k")
    if isinstance(k, str):
        try:
            k_bytes = base64.urlsafe_b64decode(k + "==")
        except Exception:
            return key
        new_key = dict(key)
        new_key["k"] = k_bytes
        return new_key
    return key


async def encrypt_jwe(plaintext: str, key: Mapping[str, Any]) -> str:
    """Encrypt *plaintext* for *key* and return the compact JWE string."""
    if not settings.enable_rfc7516:
        raise RuntimeError(f"RFC 7516 support disabled: {RFC7516_SPEC_URL}")
    norm_key = _normalize_oct_key(key)
    return await _crypto.encrypt_compact(
        payload=plaintext,
        alg=JWAAlg.DIR,
        enc=JWAAlg.A256GCM,
        key=norm_key,
    )


async def decrypt_jwe(token: str, key: Mapping[str, Any]) -> str:
    """Decrypt *token* with *key* and return the plaintext string."""
    if not settings.enable_rfc7516:
        raise RuntimeError(f"RFC 7516 support disabled: {RFC7516_SPEC_URL}")
    norm_key = _normalize_oct_key(key)
    res = await _crypto.decrypt_compact(token, dir_key=norm_key.get("k"))
    return res.plaintext.decode()


__all__ = ["encrypt_jwe", "decrypt_jwe", "RFC7516_SPEC_URL"]
