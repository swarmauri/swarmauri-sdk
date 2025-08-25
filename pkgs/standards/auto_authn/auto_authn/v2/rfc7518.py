"""RFC 7518 - JSON Web Algorithms (JWA).

Expose the list of algorithms supported by this service. Controlled via the
``AUTO_AUTHN_ENABLE_RFC7518`` environment variable.

See RFC 7518: https://www.rfc-editor.org/rfc/rfc7518
"""

from typing import Final

from swarmauri_core.crypto.types import JWAAlg

from .runtime_cfg import settings
from .rfc8812 import WEBAUTHN_ALGORITHMS

RFC7518_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7518"


def supported_algorithms() -> list[str]:
    """Return algorithms supported for JOSE operations."""
    if not settings.enable_rfc7518:
        raise RuntimeError(f"RFC 7518 support disabled: {RFC7518_SPEC_URL}")

    algs = {alg.value for alg in JWAAlg}
    if settings.enable_rfc8812:
        algs.update(WEBAUTHN_ALGORITHMS)
    else:
        # Ensure RS256 is always available even when WebAuthn algorithms are
        # disabled. This is required for OpenID Connect ID Token compliance.
        algs.add(JWAAlg.RS256.value)
    return sorted(algs)


__all__ = ["supported_algorithms", "RFC7518_SPEC_URL"]
