"""WebAuthn algorithm helpers for RFC 8812 compliance.

This module exposes the set of COSE/JOSE algorithm identifiers registered
for use with Web Authentication (WebAuthn) by :rfc:`8812`. Validation is
feature flagged via ``enable_rfc8812`` in :mod:`tigrbl_auth.runtime_cfg` so
systems may opt in or out of enforcement.

See RFC 8812: https://www.rfc-editor.org/rfc/rfc8812
"""

from __future__ import annotations

from typing import Final, FrozenSet

from . import runtime_cfg

RFC8812_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8812"

# Algorithms registered for WebAuthn. Using ``frozenset`` prevents accidental
# mutation of the registry at runtime.
WEBAUTHN_ALGORITHMS: Final[FrozenSet[str]] = frozenset(
    {
        "RS256",
        "RS384",
        "RS512",
        "RS1",
        "PS256",
        "PS384",
        "PS512",
        "ES256",
        "ES384",
        "ES512",
        "ES256K",
    }
)


def is_webauthn_algorithm(alg: object, *, enabled: bool | None = None) -> bool:
    """Return ``True`` if *alg* is registered for WebAuthn per :rfc:`8812`.

    Algorithm identifiers are compared case-insensitively to better tolerate
    input from external sources. When the feature is disabled the check always
    returns ``True`` to allow deployments to accept non-registered algorithms.
    Non-string inputs are rejected to avoid attribute errors during validation.
    """

    if enabled is None:
        enabled = runtime_cfg.settings.enable_rfc8812
    if not enabled:
        return True
    if not isinstance(alg, str):
        return False
    return alg.upper() in WEBAUTHN_ALGORITHMS


__all__ = ["is_webauthn_algorithm", "WEBAUTHN_ALGORITHMS", "RFC8812_SPEC_URL"]
