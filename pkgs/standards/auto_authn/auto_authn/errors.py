"""Custom JWT-related exceptions for auto_authn.

The auto_authn package relies on swarmauri token services and avoids direct
use of external libraries such as PyJWT.  These lightweight exception classes
provide a small surface that mirrors the errors previously exposed by PyJWT
without requiring a dependency on that package.
"""

from __future__ import annotations


class InvalidTokenError(Exception):
    """Raised when a JWT cannot be decoded or fails validation."""


class InvalidKeyError(Exception):
    """Raised when a suitable key for JWT processing cannot be found."""


__all__ = ["InvalidTokenError", "InvalidKeyError"]
