"""RFC 7515 - JSON Web Signature (JWS).

This module provides thin wrappers around :mod:`jwcrypto.jws` to create and
verify JWS objects. Functionality can be toggled via the
``AUTO_AUTHN_ENABLE_RFC7515`` environment variable.
"""

from jwcrypto import jws, jwk

from .runtime_cfg import settings


def sign_jws(payload: str, key: jwk.JWK) -> str:
    """Return a JWS compact serialization of *payload* using *key*."""
    if not settings.enable_rfc7515:
        raise RuntimeError("RFC 7515 support disabled")
    token = jws.JWS(payload.encode())
    token.add_signature(key, None, json_encode({"alg": "EdDSA"}))
    return token.serialize()


def verify_jws(token: str, key: jwk.JWK) -> str:
    """Verify *token* and return the decoded payload as a string."""
    if not settings.enable_rfc7515:
        raise RuntimeError("RFC 7515 support disabled")
    obj = jws.JWS()
    obj.deserialize(token)
    obj.verify(key)
    return obj.payload.decode()


def json_encode(data: dict) -> str:
    """Minimal JSON encoder to avoid pulling in ``json`` at import time."""
    import json

    return json.dumps(data)


__all__ = ["sign_jws", "verify_jws"]
