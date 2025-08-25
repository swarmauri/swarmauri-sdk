"""WebAuthn algorithm registrations for RFC 8812 compliance.

This module provides minimal constants and helpers for the algorithms
registered in :rfc:`8812`.  Support can be toggled via
``runtime_cfg.Settings.enable_rfc8812`` so deployments may opt out of
validation.
"""

from __future__ import annotations

from typing import Dict

from .runtime_cfg import settings

RFC8812_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8812"

#: Mapping of JOSE algorithm names to COSE numeric values as defined by RFC 8812.
WEBAUTHN_ALGORITHMS: Dict[str, int] = {
    "RS256": -257,
    "RS384": -258,
    "RS512": -259,
    "RS1": -65535,
    "ES256K": -47,
}


def is_webauthn_algorithm(name: str, *, enabled: bool | None = None) -> bool:
    """Return ``True`` if *name* is a registered WebAuthn algorithm.

    When ``enabled`` is ``False`` the check always succeeds.  If ``enabled`` is
    ``None`` the global feature toggle is used.
    """

    if enabled is None:
        enabled = settings.enable_rfc8812
    if not enabled:
        return True
    return name in WEBAUTHN_ALGORITHMS


__all__ = ["RFC8812_SPEC_URL", "WEBAUTHN_ALGORITHMS", "is_webauthn_algorithm"]
