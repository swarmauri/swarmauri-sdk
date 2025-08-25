"""EdDSA helpers for RFC 8037 compliance.

This module exposes minimal Ed25519 signing and verification utilities
inspired by :rfc:`8037`.  The feature can be disabled via the
``enable_rfc8037`` flag in :mod:`auto_authn.v2.runtime_cfg` to permit
deployments without CFRG algorithm support.
"""

from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from typing import Final

from .runtime_cfg import settings

RFC8037_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8037"


def sign_eddsa(
    message: bytes, key: Ed25519PrivateKey | bytes, *, enabled: bool | None = None
) -> bytes:
    """Return an Ed25519 signature for *message* per :rfc:`8037`.

    When ``enabled`` is ``False`` the message is returned unchanged to allow
    systems to operate without EdDSA support.
    """

    if enabled is None:
        enabled = settings.enable_rfc8037
    if not enabled:
        return message
    if isinstance(key, bytes):
        key = Ed25519PrivateKey.from_private_bytes(key)
    return key.sign(message)


def verify_eddsa(
    message: bytes,
    signature: bytes,
    key: Ed25519PublicKey | bytes,
    *,
    enabled: bool | None = None,
) -> bool:
    """Return ``True`` if *signature* is valid for *message* per :rfc:`8037`.

    When ``enabled`` is ``False`` the function always returns ``True``.
    """

    if enabled is None:
        enabled = settings.enable_rfc8037
    if not enabled:
        return True
    if isinstance(key, bytes):
        key = Ed25519PublicKey.from_public_bytes(key)
    try:
        key.verify(signature, message)
    except Exception:
        return False
    return True


__all__ = ["sign_eddsa", "verify_eddsa", "RFC8037_SPEC_URL"]
