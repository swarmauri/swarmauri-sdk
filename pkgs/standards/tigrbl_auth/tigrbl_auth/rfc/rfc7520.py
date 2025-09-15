"""JOSE composition helpers for RFC 7520 compliance.

This module demonstrates the JOSE patterns defined in :rfc:`7520`, providing
helpers that sign payloads before encrypting them and vice‑versa. Support can
be toggled via the ``TIGRBL_AUTH_ENABLE_RFC7520`` environment variable.

See RFC 7520: https://www.rfc-editor.org/rfc/rfc7520
"""

from typing import Final

from ..runtime_cfg import settings
from .rfc7515 import sign_jws, verify_jws
from .rfc7516 import encrypt_jwe, decrypt_jwe

RFC7520_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7520"


async def jws_then_jwe(payload: str, key: dict) -> str:
    """Sign *payload* then encrypt the resulting JWS."""
    if not settings.enable_rfc7520:
        raise RuntimeError(f"RFC 7520 support disabled: {RFC7520_SPEC_URL}")
    jws_token = await sign_jws(payload, key)
    return await encrypt_jwe(jws_token, key)


async def jwe_then_jws(token: str, key: dict) -> str:
    """Decrypt a JWE then verify the contained JWS."""
    if not settings.enable_rfc7520:
        raise RuntimeError(f"RFC 7520 support disabled: {RFC7520_SPEC_URL}")
    jws_token = await decrypt_jwe(token, key)
    return await verify_jws(jws_token, key)


__all__ = ["jws_then_jwe", "jwe_then_jws", "RFC7520_SPEC_URL"]
