"""Utilities for JWT Profile for OAuth 2.0 Access Tokens (RFC 9068).

This module implements minimal helpers to attach and validate the mandatory
claims defined by `RFC 9068 <https://datatracker.ietf.org/doc/html/rfc9068>`_.
It is designed to be feature-flagged via ``enable_rfc9068`` in
``runtime_cfg.Settings`` so that projects can opt in to strict compliance.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Set

from jwt.exceptions import InvalidTokenError

from .runtime_cfg import settings


def add_rfc9068_claims(
    payload: Dict[str, Any],
    *,
    issuer: str,
    audience: Iterable[str] | str,
    enabled: bool | None = None,
) -> Dict[str, Any]:
    """Return a copy of ``payload`` with RFC 9068 required claims.

    When the feature is disabled the payload is returned unchanged.  If
    ``enabled`` is ``None`` the global ``settings.enable_rfc9068`` flag is
    consulted.

    Parameters
    ----------
    payload:
        Base JWT payload to augment.
    issuer:
        Value for the ``iss`` claim identifying the authorization server.
    audience:
        Intended audience for the token. A string or iterable of strings.
    """
    if enabled is None:
        enabled = settings.enable_rfc9068
    if not enabled:
        return dict(payload)
    augmented = dict(payload)
    augmented["iss"] = issuer
    if isinstance(audience, str):
        augmented["aud"] = audience
    else:
        augmented["aud"] = list(audience)
    return augmented


def validate_rfc9068_claims(
    payload: Dict[str, Any],
    *,
    issuer: str,
    audience: Iterable[str] | str,
    enabled: bool | None = None,
) -> None:
    """Validate RFC 9068 required claims in *payload*.

    When the feature is disabled the function performs no checks.  Raises
    ``InvalidTokenError`` if any requirement is not met when enabled.
    """
    if enabled is None:
        enabled = settings.enable_rfc9068
    if not enabled:
        return
    if payload.get("iss") != issuer:
        raise InvalidTokenError("issuer mismatch per RFC 9068")
    token_aud = payload.get("aud")
    expected: Set[str] = {audience} if isinstance(audience, str) else set(audience)
    presented: Set[str] = (
        {token_aud} if isinstance(token_aud, str) else set(token_aud or [])
    )
    if not (expected & presented):
        raise InvalidTokenError("audience mismatch per RFC 9068")
    for claim in ("sub", "exp"):
        if claim not in payload:
            raise InvalidTokenError(f"{claim} claim required by RFC 9068")
