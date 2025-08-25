"""WebAuthn algorithm helpers for RFC 8812 compliance.

This module exposes the set of COSE/JOSE algorithm identifiers registered
for use with Web Authentication (WebAuthn) by :rfc:`8812`. Validation is
feature flagged via ``enable_rfc8812`` in :mod:`auto_authn.v2.runtime_cfg` so
systems may opt in or out of enforcement.

See RFC 8812: https://www.rfc-editor.org/rfc/rfc8812
"""

from __future__ import annotations

from typing import Final

from .runtime_cfg import settings

RFC8812_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8812"

WEBAUTHN_ALGORITHMS: Final[set[str]] = {"RS256", "RS384", "RS512", "RS1", "ES256K"}


def is_webauthn_algorithm(alg: str, *, enabled: bool | None = None) -> bool:
    """Return ``True`` if *alg* is registered for WebAuthn per :rfc:`8812`.

    When the feature is disabled the check always returns ``True`` to allow
    deployments to accept non-registered algorithms.
    """

    if enabled is None:
        enabled = settings.enable_rfc8812
    if not enabled:
        return True
    return alg in WEBAUTHN_ALGORITHMS


__all__ = ["is_webauthn_algorithm", "WEBAUTHN_ALGORITHMS", "RFC8812_SPEC_URL"]
