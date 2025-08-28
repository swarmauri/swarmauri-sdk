"""RFC 7519 - JSON Web Token (JWT).

Convenience wrappers around :class:`auto_authn.jwtoken.JWTCoder` that can be
enabled or disabled via ``AUTO_AUTHN_ENABLE_RFC7519``.

See RFC 7519: https://www.rfc-editor.org/rfc/rfc7519
"""

from typing import Final

from .jwtoken import JWTCoder
from .runtime_cfg import settings

RFC7519_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7519"


def encode_jwt(**claims) -> str:
    """Encode *claims* as a JWT string."""
    if not settings.enable_rfc7519:
        raise RuntimeError(f"RFC 7519 support disabled: {RFC7519_SPEC_URL}")
    sub = claims.pop("sub", "")
    return JWTCoder.default().sign(sub=sub, **claims)


def decode_jwt(token: str) -> dict:
    """Decode and verify *token* returning the claims dictionary."""
    if not settings.enable_rfc7519:
        raise RuntimeError(f"RFC 7519 support disabled: {RFC7519_SPEC_URL}")
    return JWTCoder.default().decode(token)


__all__ = ["encode_jwt", "decode_jwt", "RFC7519_SPEC_URL"]
