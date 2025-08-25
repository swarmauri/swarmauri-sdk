"""Web Push message encryption helpers for RFC 8291 compliance.

This module offers minimal AES-128-GCM helpers inspired by
:rfc:`8291`. The encryption utilities can be disabled via the
``enable_rfc8291`` flag in :mod:`auto_authn.v2.runtime_cfg` to allow
unencrypted operation in constrained environments.

See RFC 8291: https://www.rfc-editor.org/rfc/rfc8291
"""

from __future__ import annotations

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Final

from .runtime_cfg import settings

RFC8291_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8291"


def encrypt_push_message(
    plaintext: bytes, key: bytes, nonce: bytes, *, enabled: bool | None = None
) -> bytes:
    """Return ciphertext for *plaintext* using AES-128-GCM per :rfc:`8291`.

    When ``enabled`` is ``False`` the plaintext is returned unchanged.  The
    *key* must be 16 bytes and *nonce* 12 bytes as required by the spec.
    """

    if enabled is None:
        enabled = settings.enable_rfc8291
    if not enabled:
        return plaintext
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(nonce, plaintext, associated_data=None)


def decrypt_push_message(
    ciphertext: bytes, key: bytes, nonce: bytes, *, enabled: bool | None = None
) -> bytes:
    """Return plaintext for *ciphertext* encrypted by :func:`encrypt_push_message`.

    When ``enabled`` is ``False`` the ciphertext is returned unchanged.
    """

    if enabled is None:
        enabled = settings.enable_rfc8291
    if not enabled:
        return ciphertext
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None)


__all__ = ["encrypt_push_message", "decrypt_push_message", "RFC8291_SPEC_URL"]
