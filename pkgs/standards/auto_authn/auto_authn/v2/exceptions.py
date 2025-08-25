"""Custom exception types for JWT handling in ``auto_authn``.

These exceptions mirror the most commonly used errors from the external
``jwt`` package so that the rest of the codebase and tests no longer need to
depend on that library directly.
"""

from __future__ import annotations


class JWTError(Exception):
    """Base class for JWT-related errors."""


class InvalidTokenError(JWTError):
    """Raised when a token cannot be decoded or fails validation."""


class InvalidKeyError(InvalidTokenError):
    """Raised when a verification key cannot be resolved."""


__all__ = ["JWTError", "InvalidTokenError", "InvalidKeyError"]
