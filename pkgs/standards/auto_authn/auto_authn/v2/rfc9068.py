"""Utilities for JWT Profile for OAuth 2.0 Access Tokens (RFC 9068).

This module implements minimal helpers to attach and validate the mandatory
claims defined by `RFC 9068 <https://datatracker.ietf.org/doc/html/rfc9068>`_.
It is designed to be feature-flagged via ``enable_rfc9068`` in
``runtime_cfg.Settings`` so that projects can opt in to strict compliance.
"""

from __future__ import annotations

from typing import Any, Dict, Final, Iterable, Set

from jwt.exceptions import InvalidTokenError

RFC9068_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc9068"


def add_rfc9068_claims(
    payload: Dict[str, Any], *, issuer: str, audience: Iterable[str] | str
) -> Dict[str, Any]:
    """Return a copy of ``payload`` with RFC 9068 required claims.

    Parameters
    ----------
    payload:
        Base JWT payload to augment.
    issuer:
        Value for the ``iss`` claim identifying the authorization server.
    audience:
        Intended audience for the token. A string or iterable of strings.
    """
    augmented = dict(payload)
    augmented["iss"] = issuer
    if isinstance(audience, str):
        augmented["aud"] = audience
    else:
        augmented["aud"] = list(audience)
    return augmented


def validate_rfc9068_claims(
    payload: Dict[str, Any], *, issuer: str, audience: Iterable[str] | str
) -> None:
    """Validate RFC 9068 required claims in *payload*.

    Raises ``InvalidTokenError`` if any requirement is not met.
    """
    if payload.get("iss") != issuer:
        raise InvalidTokenError(f"issuer mismatch per RFC 9068: {RFC9068_SPEC_URL}")
    token_aud = payload.get("aud")
    expected: Set[str] = {audience} if isinstance(audience, str) else set(audience)
    presented: Set[str] = (
        {token_aud} if isinstance(token_aud, str) else set(token_aud or [])
    )
    if not (expected & presented):
        raise InvalidTokenError(f"audience mismatch per RFC 9068: {RFC9068_SPEC_URL}")
    for claim in ("sub", "exp"):
        if claim not in payload:
            raise InvalidTokenError(
                f"{claim} claim required by RFC 9068: {RFC9068_SPEC_URL}"
            )


__all__ = ["add_rfc9068_claims", "validate_rfc9068_claims", "RFC9068_SPEC_URL"]
