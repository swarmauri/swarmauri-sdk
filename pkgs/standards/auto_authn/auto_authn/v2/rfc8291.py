"""Utilities for RFC 8291 - Message Encryption for Web Push.

This module implements a toy symmetric "encryption" routine to illustrate
how Web Push message encryption could be toggled within the library. The
cryptographic operations here are placeholders and not suitable for real use.
"""

from __future__ import annotations

from .runtime_cfg import settings

RFC8291_SPEC_URL = "https://datatracker.ietf.org/doc/html/rfc8291"


def encrypt_push_message(message: str) -> str:
    """Encrypt a message when RFC 8291 support is enabled.

    The implementation simply reverses the string and should not be used for
    production encryption. It serves only to demonstrate modular RFC support.
    """
    if not settings.enable_rfc8291:
        raise NotImplementedError("RFC 8291 support is disabled")
    return message[::-1]


def decrypt_push_message(ciphertext: str) -> str:
    """Decrypt a message previously processed by :func:`encrypt_push_message`."""
    if not settings.enable_rfc8291:
        raise NotImplementedError("RFC 8291 support is disabled")
    return ciphertext[::-1]
