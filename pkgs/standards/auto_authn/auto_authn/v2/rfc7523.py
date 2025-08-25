"""RFC 7523 - JSON Web Token (JWT) Bearer Token Profile for OAuth 2.0.

Helpers for creating and verifying JWT bearer assertions. This feature can be
turned on or off with the ``AUTO_AUTHN_ENABLE_RFC7523`` environment variable.
"""

from .runtime_cfg import settings
from .rfc7519 import encode_jwt, decode_jwt

RFC7523_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc7523"


def create_jwt_bearer_assertion(**claims) -> str:
    """Return a JWT bearer assertion containing *claims* per RFC 7523."""
    if not settings.enable_rfc7523:
        raise RuntimeError("RFC 7523 support disabled")
    return encode_jwt(**claims)


def verify_jwt_bearer_assertion(token: str) -> dict:
    """Decode *token* and return the claims dictionary."""
    if not settings.enable_rfc7523:
        raise RuntimeError("RFC 7523 support disabled")
    return decode_jwt(token)


__all__ = [
    "create_jwt_bearer_assertion",
    "verify_jwt_bearer_assertion",
    "RFC7523_SPEC_URL",
]
