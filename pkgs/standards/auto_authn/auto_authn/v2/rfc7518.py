"""RFC 7518 - JSON Web Algorithms (JWA).

Expose the list of algorithms supported by this service. Controlled via the
``AUTO_AUTHN_ENABLE_RFC7518`` environment variable.

See RFC 7518: https://www.rfc-editor.org/rfc/rfc7518
"""

from typing import Final

from .runtime_cfg import settings

RFC7518_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7518"


def supported_algorithms() -> list[str]:
    """Return algorithms supported for JOSE operations."""
    if not settings.enable_rfc7518:
        raise RuntimeError(f"RFC 7518 support disabled: {RFC7518_SPEC_URL}")
    return ["EdDSA"]


__all__ = ["supported_algorithms", "RFC7518_SPEC_URL"]
