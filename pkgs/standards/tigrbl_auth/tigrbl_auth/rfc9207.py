"""Utilities for OAuth 2.0 Authorization Server Issuer Identification (RFC 9207).

This module validates the ``iss`` parameter returned in the authorization
response as described by RFC 9207. Support for this feature can be toggled via
``settings.enable_rfc9207``.

See RFC 9207: https://www.rfc-editor.org/rfc/rfc9207
"""

from __future__ import annotations

from typing import Mapping

from .runtime_cfg import settings

RFC9207_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc9207"


def extract_issuer(params: Mapping[str, str], expected_issuer: str) -> str:
    """Return the issuer identifier from ``params`` after validation.

    Raises ``NotImplementedError`` if RFC 9207 support is disabled via runtime
    settings. Raises ``ValueError`` if the ``iss`` parameter is missing or does
    not match ``expected_issuer``.
    """

    if not settings.enable_rfc9207:
        raise NotImplementedError(
            f"issuer identification not enabled: {RFC9207_SPEC_URL}"
        )

    issuer = params.get("iss")
    if issuer is None:
        raise ValueError(f"missing iss parameter: {RFC9207_SPEC_URL}")
    if issuer != expected_issuer:
        raise ValueError(f"issuer mismatch: {RFC9207_SPEC_URL}")
    return issuer


__all__ = ["extract_issuer", "RFC9207_SPEC_URL"]
