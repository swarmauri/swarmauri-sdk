"""RFC 7519 - JSON Web Token (JWT).

Convenience wrappers around :class:`auto_authn.v2.jwtoken.JWTCoder` that can be
enabled or disabled via ``AUTO_AUTHN_ENABLE_RFC7519``.
"""

from .jwtoken import JWTCoder
from .runtime_cfg import settings


def encode_jwt(**claims) -> str:
    """Encode *claims* as a JWT string."""
    if not settings.enable_rfc7519:
        raise RuntimeError("RFC 7519 support disabled")
    return JWTCoder.default().sign(**claims)


def decode_jwt(token: str) -> dict:
    """Decode and verify *token* returning the claims dictionary."""
    if not settings.enable_rfc7519:
        raise RuntimeError("RFC 7519 support disabled")
    return JWTCoder.default().decode(token)


__all__ = ["encode_jwt", "decode_jwt"]
