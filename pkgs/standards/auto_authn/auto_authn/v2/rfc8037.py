"""Minimal Ed25519 signing utilities via swarmauri plugins (RFC 8037)."""

from __future__ import annotations

import asyncio

from .deps import Ed25519EnvelopeSigner

from .runtime_cfg import settings

RFC8037_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8037"
_signer = Ed25519EnvelopeSigner()


def sign_eddsa(message: bytes, key: bytes, *, enabled: bool | None = None) -> bytes:
    """Return an Ed25519 signature for *message* per RFC 8037."""
    if enabled is None:
        enabled = settings.enable_rfc8037
    if not enabled:
        return message
    sigs = asyncio.run(
        _signer.sign_bytes({"kind": "raw_ed25519_sk", "bytes": key}, message)
    )
    return sigs[0]["sig"]  # type: ignore[index]


def verify_eddsa(
    message: bytes,
    signature: bytes,
    key: bytes,
    *,
    enabled: bool | None = None,
) -> bool:
    """Return ``True`` if *signature* is valid for *message* per RFC 8037."""
    if enabled is None:
        enabled = settings.enable_rfc8037
    if not enabled:
        return True
    return asyncio.run(
        _signer.verify_bytes(
            message,
            [{"alg": "Ed25519", "sig": signature}],
            opts={"pubkeys": [key]},
        )
    )


__all__ = ["sign_eddsa", "verify_eddsa", "RFC8037_SPEC_URL"]
