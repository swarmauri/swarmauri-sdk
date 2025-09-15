"""Authentication Method References ("amr") utilities for RFC 8176 compliance.

This module provides helpers for validating the ``amr`` (Authentication Method
References) claim values as defined in :rfc:`8176`.  Validation can be
disabled via the ``enable_rfc8176`` flag in :mod:`tigrbl_auth.runtime_cfg` to
allow acceptance of non-standard values.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from ..runtime_cfg import settings

RFC8176_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8176"

# Common Authentication Method Reference values from RFC 8176
AMR_VALUES: set[str] = {
    "face",
    "fpt",
    "geo",
    "hwk",
    "iris",
    "kba",
    "mca",
    "mfa",
    "otp",
    "pin",
    "pwd",
    "rba",
    "retina",
    "sc",
    "sms",
    "swk",
    "tel",
    "user",
    "vbm",
    "wia",
}


def validate_amr_claim(amr: Sequence[str], *, enabled: bool | None = None) -> bool:
    """Return ``True`` if all *amr* values are registered per :rfc:`8176`.

    When ``enabled`` is ``False`` the list is considered valid regardless of
    its contents.
    """

    if enabled is None:
        enabled = settings.enable_rfc8176
    if not enabled:
        return True
    return all(value in AMR_VALUES for value in amr)


__all__ = ["validate_amr_claim", "AMR_VALUES", "RFC8176_SPEC_URL"]
