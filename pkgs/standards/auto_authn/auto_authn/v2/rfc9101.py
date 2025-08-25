"""Utilities for JWT-Secured Authorization Request (RFC 9101).

This module provides helpers to encode and decode authorization request
parameters as JSON Web Tokens (JWT) per RFC 9101 \u00a72.1. The feature can be
turned on or off using ``settings.enable_rfc9101``.

See RFC 9101: https://www.rfc-editor.org/rfc/rfc9101
"""

from __future__ import annotations

from typing import Any, Dict, Final, Iterable, Tuple
import asyncio
import json
from base64 import urlsafe_b64decode, urlsafe_b64encode

from .deps import (
    ExportPolicy,
    JWAAlg,
    JWTTokenService,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
    LocalKeyProvider,
)

from .runtime_cfg import settings

RFC9101_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc9101"


def _svc_for_secret(secret: str, algorithm: str) -> Tuple[JWTTokenService, str]:
    if algorithm != "HS256":
        raise ValueError("Only HS256 is supported")
    kp = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.HMAC_SHA256,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="request_obj",
    )
    ref = asyncio.run(kp.import_key(spec, secret.encode()))

    async def jwks() -> dict:
        k = urlsafe_b64encode(secret.encode()).rstrip(b"=").decode()
        return {
            "keys": [
                {
                    "kty": "oct",
                    "alg": "HS256",
                    "k": k,
                    "kid": f"{ref.kid}.{ref.version}",
                }
            ]
        }

    kp.jwks = jwks  # type: ignore[assignment]
    return JWTTokenService(kp), ref.kid


def _token_alg(token: str) -> str | None:
    """Return the ``alg`` value from a compact JWT without verification."""
    try:
        header_b64, _payload, _sig = token.split(".")
        padded = header_b64 + "=" * (-len(header_b64) % 4)
        header = json.loads(urlsafe_b64decode(padded))
    except Exception:
        return None
    return header.get("alg")


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
    svc, kid = _svc_for_secret(secret, algorithm)
    alg = JWAAlg(algorithm)
    return asyncio.run(svc.mint(params, alg=alg, kid=kid, lifetime_s=None))


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

    alg = _token_alg(token)
    if alg is None:
        raise ValueError("Could not determine JWT algorithm")
    if algorithms is not None and alg not in set(algorithms):
        raise ValueError(f"Unsupported JWT algorithm: {alg}")

    svc, _kid = _svc_for_secret(secret, alg)
    claims = asyncio.run(svc.verify(token, audience=None, issuer=None, leeway_s=60))
    claims.pop("iat", None)
    claims.pop("nbf", None)
    return claims


__all__ = ["create_request_object", "parse_request_object", "RFC9101_SPEC_URL"]
