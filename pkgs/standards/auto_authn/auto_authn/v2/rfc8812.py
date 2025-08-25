"""COSE and JOSE Registrations for Web Authentication (RFC 8812).

Provides a helper to check whether a COSE algorithm identifier is among those
registered for WebAuthn by `RFC 8812 <https://datatracker.ietf.org/doc/html/rfc8812>`_.
The check is gated by ``enable_rfc8812`` in :mod:`auto_authn.v2.runtime_cfg`.
"""

from __future__ import annotations

from .runtime_cfg import settings

RFC8812_SPEC_URL = "https://datatracker.ietf.org/doc/html/rfc8812"

# Algorithm identifiers registered by RFC 8812
RFC8812_ALGORITHMS = {-257, -258, -259, -65535, -47}


def is_supported_cose_alg(alg: int) -> bool:
    """Return True if *alg* is registered for WebAuthn per RFC 8812.

    When disabled, this function always returns ``False``.
    """
    if not settings.enable_rfc8812:
        return False
    return alg in RFC8812_ALGORITHMS


__all__ = ["is_supported_cose_alg", "RFC8812_SPEC_URL", "RFC8812_ALGORITHMS"]
