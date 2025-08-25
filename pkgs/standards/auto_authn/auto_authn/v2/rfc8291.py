"""Message Encryption for Web Push (RFC 8291).

This module exposes small helpers for AES-128-GCM encryption used in Web Push
messages. Support is controlled by ``enable_rfc8291`` in
:mod:`auto_authn.v2.runtime_cfg`.
"""

from __future__ import annotations

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .runtime_cfg import settings

RFC8291_SPEC_URL = "https://datatracker.ietf.org/doc/html/rfc8291"


def encrypt_webpush(message: bytes, key: bytes, nonce: bytes) -> bytes:
    """Encrypt *message* using AES-128-GCM.

    Returns the ciphertext. If the feature is disabled the plaintext is
    returned unchanged.
    """
    if not settings.enable_rfc8291:
        return message
    aes = AESGCM(key)
    return aes.encrypt(nonce, message, None)


def decrypt_webpush(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Decrypt a ciphertext produced by :func:`encrypt_webpush`.

    If the feature is disabled the ciphertext is returned as-is.
    """
    if not settings.enable_rfc8291:
        return ciphertext
    aes = AESGCM(key)
    return aes.decrypt(nonce, ciphertext, None)


__all__ = ["encrypt_webpush", "decrypt_webpush", "RFC8291_SPEC_URL"]
