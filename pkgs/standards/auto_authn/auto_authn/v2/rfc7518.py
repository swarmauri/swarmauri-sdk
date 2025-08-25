"""RFC 7518 - JSON Web Algorithms (JWA).

Expose the list of algorithms supported by this service. Controlled via the
``AUTO_AUTHN_ENABLE_RFC7518`` environment variable.
"""

from .runtime_cfg import settings


def supported_algorithms() -> list[str]:
    """Return algorithms supported for JOSE operations."""
    if not settings.enable_rfc7518:
        raise RuntimeError("RFC 7518 support disabled")
    return ["EdDSA"]


__all__ = ["supported_algorithms"]
