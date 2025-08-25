"""Client-Initiated Backchannel Authentication (CIBA) helpers for RFC 8812 compliance.

This module provides a minimal validator for CIBA requests. The validation can
be toggled via the ``enable_rfc8812`` flag in :mod:`auto_authn.v2.runtime_cfg`.

See RFC 8812: https://www.rfc-editor.org/rfc/rfc8812
"""

from __future__ import annotations

from typing import Any, Mapping, Final

from .runtime_cfg import settings

RFC8812_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8812"


def validate_ciba_request(
    request: Mapping[str, Any], *, enabled: bool | None = None
) -> bool:
    """Return ``True`` when *request* contains an end-user hint per :rfc:`8812`.

    The specification requires that at least one of ``login_hint``,
    ``id_token_hint`` or ``login_hint_token`` is supplied. When ``enabled`` is
    ``False`` (or the global setting disables RFC 8812), the function returns
    ``True`` regardless of the request content.
    """

    if enabled is None:
        enabled = settings.enable_rfc8812
    if not enabled:
        return True
    return any(
        hint in request for hint in ("login_hint", "id_token_hint", "login_hint_token")
    )


__all__ = ["validate_ciba_request", "RFC8812_SPEC_URL"]
