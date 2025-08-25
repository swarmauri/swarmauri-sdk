"""Utilities for JWT-Secured Authorization Request (RFC 9101).

This module provides helpers to encode and decode authorization request
parameters as JSON Web Tokens (JWT) per RFC 9101 \u00a72.1. The feature can be
turned on or off using ``settings.enable_rfc9101``.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

import jwt

from .runtime_cfg import settings


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
        raise RuntimeError("RFC 9101 support disabled")
    return jwt.encode(params, secret, algorithm=algorithm)


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
        raise RuntimeError("RFC 9101 support disabled")
    algs = list(algorithms) if algorithms is not None else ["HS256"]
    return jwt.decode(token, secret, algorithms=algs)


__all__ = ["create_request_object", "parse_request_object"]
