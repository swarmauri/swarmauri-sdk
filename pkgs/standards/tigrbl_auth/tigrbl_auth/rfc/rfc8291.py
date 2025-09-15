"""Web Push message encryption helpers for RFC 8291 compliance.

This module offers minimal AES-128-GCM helpers inspired by
:rfc:`8291`. The encryption utilities can be disabled via the
``enable_rfc8291`` flag in :mod:`tigrbl_auth.runtime_cfg` to allow
unencrypted operation in constrained environments.

See RFC 8291: https://www.rfc-editor.org/rfc/rfc8291
"""

from __future__ import annotations

from typing import Final

from swarmauri_core.crypto.types import (
    AEADCiphertext,
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_crypto_paramiko import ParamikoCrypto

from ..runtime_cfg import settings

RFC8291_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8291"
_ALG: Final = "AES-256-GCM"


_crypto = ParamikoCrypto()


def _key_ref(key: bytes) -> KeyRef:
    """Return a minimal :class:`KeyRef` for *key* bytes."""

    return KeyRef(
        kid="rfc8291-key",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=key,
    )


async def encrypt_push_message(
    plaintext: bytes, key: bytes, nonce: bytes, *, enabled: bool | None = None
) -> bytes:
    """Return ciphertext for *plaintext* using AES-GCM per :rfc:`8291`.

    When ``enabled`` is ``False`` the plaintext is returned unchanged.  The
    *key* must be 16 bytes and *nonce* 12 bytes as required by the spec.
    """

    if enabled is None:
        enabled = settings.enable_rfc8291
    if not enabled:
        return plaintext
    if len(key) != 16:
        raise ValueError("RFC 8291 requires a 16-byte key")
    if len(nonce) != 12:
        raise ValueError("RFC 8291 requires a 12-byte nonce")
    key_ref = _key_ref(key)
    res = await _crypto.encrypt(key=key_ref, pt=plaintext, nonce=nonce)
    return res.ct + res.tag


async def decrypt_push_message(
    ciphertext: bytes, key: bytes, nonce: bytes, *, enabled: bool | None = None
) -> bytes:
    """Return plaintext for *ciphertext* encrypted by :func:`encrypt_push_message`.

    When ``enabled`` is ``False`` the ciphertext is returned unchanged.
    """

    if enabled is None:
        enabled = settings.enable_rfc8291
    if not enabled:
        return ciphertext
    if len(key) != 16:
        raise ValueError("RFC 8291 requires a 16-byte key")
    if len(nonce) != 12:
        raise ValueError("RFC 8291 requires a 12-byte nonce")
    key_ref = _key_ref(key)
    ct = AEADCiphertext(
        kid=key_ref.kid,
        version=key_ref.version,
        alg=_ALG,
        nonce=nonce,
        ct=ciphertext[:-16],
        tag=ciphertext[-16:],
    )
    return await _crypto.decrypt(key=key_ref, ct=ct)


__all__ = ["encrypt_push_message", "decrypt_push_message", "RFC8291_SPEC_URL"]
