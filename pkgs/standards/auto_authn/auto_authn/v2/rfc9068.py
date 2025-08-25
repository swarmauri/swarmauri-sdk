"""JWT Profile for OAuth 2.0 Access Tokens (RFC 9068).

This module provides helpers for validating that decoded access token
payloads comply with the requirements of :rfc:`9068`. Validation is
optional and controlled via the ``enable_rfc9068`` flag in
:mod:`runtime_cfg`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping, Any

from .runtime_cfg import settings

__all__ = [
    "RFC9068Error",
    "validate_jwt_access_token",
    "enforce_jwt_access_token",
    "is_enabled",
]


class RFC9068Error(ValueError):
    """Error raised for RFC 9068 validation failures."""


REQUIRED_CLAIMS = {"iss", "sub", "aud", "exp", "iat"}


def _to_datetime(value: Any) -> datetime:
    """Return ``value`` as an aware ``datetime``."""

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, datetime):
        return value
    raise TypeError("timestamp required")


def is_enabled() -> bool:
    """Return ``True`` if RFC 9068 enforcement is active."""

    return settings.enable_rfc9068


def validate_jwt_access_token(claims: Mapping[str, Any]) -> None:
    """Validate *claims* according to RFC 9068.

    Ensures all required claims are present and that ``exp`` is greater than
    ``iat``.
    """

    missing = REQUIRED_CLAIMS.difference(claims)
    if missing:
        raise RFC9068Error(f"missing required claims: {', '.join(sorted(missing))}")

    exp = _to_datetime(claims["exp"])
    iat = _to_datetime(claims["iat"])
    if exp <= iat:
        raise RFC9068Error("exp must be later than iat")


def enforce_jwt_access_token(claims: Mapping[str, Any]) -> None:
    """Validate *claims* when RFC 9068 enforcement is enabled."""

    if not is_enabled():
        return
    validate_jwt_access_token(claims)
