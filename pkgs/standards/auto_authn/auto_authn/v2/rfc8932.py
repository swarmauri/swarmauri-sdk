"""Utilities for DNS privacy compliance (RFC 8932).

This module enforces that DNS queries use encrypted transports as
recommended by RFC 8932. Support for this feature can be toggled via
``settings.enable_rfc8932``.

See RFC 8932: https://www.rfc-editor.org/rfc/rfc8932
"""

from __future__ import annotations

from .runtime_cfg import settings

RFC8932_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8932"


def enforce_encrypted_dns(transport: str) -> str:
    """Validate that ``transport`` is an encrypted DNS transport.

    Raises ``NotImplementedError`` if RFC 8932 support is disabled via
    runtime settings. Raises ``ValueError`` if ``transport`` does not
    represent an encrypted DNS protocol (DoT or DoH).
    """

    if not settings.enable_rfc8932:
        raise NotImplementedError(
            f"dns privacy enforcement not enabled: {RFC8932_SPEC_URL}"
        )
    if transport not in {"DoT", "DoH"}:
        raise ValueError(f"unencrypted dns transport: {RFC8932_SPEC_URL}")
    return transport


__all__ = ["enforce_encrypted_dns", "RFC8932_SPEC_URL"]
