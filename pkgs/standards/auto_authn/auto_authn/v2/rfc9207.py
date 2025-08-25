"""Utilities for OAuth 2.0 Authorization Server Issuer Identification (RFC 9207).

This module validates the ``iss`` parameter returned in the authorization
response as described by RFC 9207. Support for this feature can be toggled via
``settings.enable_rfc9207``.
"""

from __future__ import annotations

from typing import Mapping

from .runtime_cfg import settings


def extract_issuer(params: Mapping[str, str], expected_issuer: str) -> str:
    """Return the issuer identifier from ``params`` after validation.

    Raises ``NotImplementedError`` if RFC 9207 support is disabled via runtime
    settings. Raises ``ValueError`` if the ``iss`` parameter is missing or does
    not match ``expected_issuer``.
    """

    if not settings.enable_rfc9207:
        raise NotImplementedError("issuer identification not enabled")

    issuer = params.get("iss")
    if issuer is None:
        raise ValueError("missing iss parameter")
    if issuer != expected_issuer:
        raise ValueError("issuer mismatch")
    return issuer


__all__ = ["extract_issuer"]
