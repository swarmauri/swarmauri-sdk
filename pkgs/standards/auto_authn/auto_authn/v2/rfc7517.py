"""RFC 7517 - JSON Web Key (JWK).

Utility helpers for exporting the service's Ed25519 key pair as JWKs. These
helpers respect the ``AUTO_AUTHN_ENABLE_RFC7517`` feature flag.
"""

from jwcrypto import jwk

from .crypto import public_key, signing_key
from .runtime_cfg import settings


def load_signing_jwk() -> jwk.JWK:
    """Return the private signing key as a :class:`~jwcrypto.jwk.JWK`."""
    if not settings.enable_rfc7517:
        raise RuntimeError("RFC 7517 support disabled")
    return jwk.JWK.from_pem(signing_key())


def load_public_jwk() -> jwk.JWK:
    """Return the public key as a :class:`~jwcrypto.jwk.JWK`."""
    if not settings.enable_rfc7517:
        raise RuntimeError("RFC 7517 support disabled")
    return jwk.JWK.from_pem(public_key())


__all__ = ["load_signing_jwk", "load_public_jwk"]
