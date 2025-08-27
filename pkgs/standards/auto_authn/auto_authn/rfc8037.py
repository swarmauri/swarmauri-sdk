"""Minimal Ed25519 signing utilities via swarmauri plugins (RFC 8037)."""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable

from .deps import Ed25519EnvelopeSigner
from .runtime_cfg import settings

try:  # pragma: no cover - optional dependency
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
except Exception:  # pragma: no cover - runtime check
    Ed25519PrivateKey = Ed25519PublicKey = object  # type: ignore[assignment]

RFC8037_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8037"
_signer = Ed25519EnvelopeSigner()


def _run(coro: Awaitable[Any]) -> Any:
    """Run *coro* even if an event loop is already running."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _to_keyref(key: bytes | Ed25519PrivateKey) -> dict[str, object]:
    if isinstance(key, (bytes, bytearray)):
        return {"kind": "raw_ed25519_sk", "bytes": key}
    return {"kind": "cryptography_obj", "obj": key}


def sign_eddsa(
    message: bytes, key: bytes | Ed25519PrivateKey, *, enabled: bool | None = None
) -> bytes:
    """Return an Ed25519 signature for *message* per RFC 8037."""
    if enabled is None:
        enabled = settings.enable_rfc8037
    if not enabled:
        return message
    sigs = _run(_signer.sign_bytes(_to_keyref(key), message))
    return sigs[0]["sig"]  # type: ignore[index]


def verify_eddsa(
    message: bytes,
    signature: bytes,
    key: bytes | Ed25519PublicKey,
    *,
    enabled: bool | None = None,
) -> bool:
    """Return ``True`` if *signature* is valid for *message* per RFC 8037."""
    if enabled is None:
        enabled = settings.enable_rfc8037
    if not enabled:
        return True
    return bool(
        _run(
            _signer.verify_bytes(
                message,
                [{"alg": "Ed25519", "sig": signature}],
                opts={"pubkeys": [key]},
            ),
        )
    )


__all__ = ["sign_eddsa", "verify_eddsa", "RFC8037_SPEC_URL"]
