"""RFC 7520 - Examples of Protecting Content Using JOSE.

Provides simple composition helpers that demonstrate signing followed by
encryption and the reverse. Controlled via the
``AUTO_AUTHN_ENABLE_RFC7520`` environment variable.
"""

from jwcrypto import jwk

from .runtime_cfg import settings
from .rfc7515 import sign_jws, verify_jws
from .rfc7516 import encrypt_jwe, decrypt_jwe


def jws_then_jwe(payload: str, key: jwk.JWK) -> str:
    """Sign *payload* then encrypt the resulting JWS."""
    if not settings.enable_rfc7520:
        raise RuntimeError("RFC 7520 support disabled")
    jws_token = sign_jws(payload, key)
    return encrypt_jwe(jws_token, key)


def jwe_then_jws(token: str, key: jwk.JWK) -> str:
    """Decrypt a JWE then verify the contained JWS."""
    if not settings.enable_rfc7520:
        raise RuntimeError("RFC 7520 support disabled")
    jws_token = decrypt_jwe(token, key)
    return verify_jws(jws_token, key)


__all__ = ["jws_then_jwe", "jwe_then_jws"]
