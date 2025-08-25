"""RFC 7517 - JSON Web Key (JWK) utilities using swarmauri key providers."""

from __future__ import annotations

import asyncio
import base64
from typing import Final

from .crypto import _load_keypair, _provider
from .runtime_cfg import settings

RFC7517_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7517"


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def load_signing_jwk() -> dict:
    """Return the private signing key as a JWK mapping."""
    if not settings.enable_rfc7517:
        raise RuntimeError(f"RFC 7517 support disabled: {RFC7517_SPEC_URL}")
    kid, priv, pub = _load_keypair()
    kp = _provider()
    ref = asyncio.run(kp.get_key(kid, include_secret=True))
    sk = ref.material or priv
    pk = ref.public or pub
    d = sk[:32] if len(sk) > 32 else sk
    return {"kty": "OKP", "crv": "Ed25519", "d": _b64u(d), "x": _b64u(pk)}


def load_public_jwk() -> dict:
    """Return the public key as a JWK mapping."""
    if not settings.enable_rfc7517:
        raise RuntimeError(f"RFC 7517 support disabled: {RFC7517_SPEC_URL}")
    kid, _, _ = _load_keypair()
    kp = _provider()
    return asyncio.run(kp.get_public_jwk(kid))


__all__ = ["load_signing_jwk", "load_public_jwk", "RFC7517_SPEC_URL"]
