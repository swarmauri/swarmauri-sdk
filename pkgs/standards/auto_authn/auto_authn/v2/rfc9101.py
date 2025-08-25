"""Utilities for JWT-Secured Authorization Request (RFC 9101).

This module provides helpers to encode and decode authorization request
parameters as JSON Web Tokens (JWT) per RFC 9101 \u00a72.1. The feature can be
turned on or off using ``settings.enable_rfc9101``.

See RFC 9101: https://www.rfc-editor.org/rfc/rfc9101
"""

from __future__ import annotations

from typing import Any, Dict, Final, Iterable
import asyncio
import json

from .deps import JWAAlg, JwsSignerVerifier

from .runtime_cfg import settings

RFC9101_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc9101"
_signer = JwsSignerVerifier()


def create_request_object(
    params: Dict[str, Any], *, secret: str, algorithm: str = "HS256"
) -> str:
    """Return a JWT request object representing ``params``.

    Raises
    ------
    RuntimeError
        If RFC 9101 support is disabled via ``settings.enable_rfc9101``.
    """
    if not settings.enable_rfc9101:
        raise RuntimeError(f"RFC 9101 support disabled: {RFC9101_SPEC_URL}")
    alg = JWAAlg(algorithm)
    key = {"kind": "raw", "key": secret}
    return asyncio.run(
        _signer.sign_compact(payload=params, alg=alg, key=key, typ="JWT")
    )


def parse_request_object(
    token: str, *, secret: str, algorithms: Iterable[str] | None = None
) -> Dict[str, Any]:
    """Decode ``token`` into authorization request parameters.

    Raises
    ------
    RuntimeError
        If RFC 9101 support is disabled via ``settings.enable_rfc9101``.
    """
    if not settings.enable_rfc9101:
        raise RuntimeError(f"RFC 9101 support disabled: {RFC9101_SPEC_URL}")

    alg_allowlist = None
    if algorithms is not None:
        alg_allowlist = [JWAAlg(a) for a in algorithms]
    result = asyncio.run(
        _signer.verify_compact(
            token,
            hmac_keys=[{"kind": "raw", "key": secret}],
            alg_allowlist=alg_allowlist,
        )
    )
    return json.loads(result.payload.decode())


__all__ = ["create_request_object", "parse_request_object", "RFC9101_SPEC_URL"]
