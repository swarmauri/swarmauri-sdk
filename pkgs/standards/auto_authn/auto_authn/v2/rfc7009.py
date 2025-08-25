"""Utilities for OAuth 2.0 Token Revocation (RFC 7009).

This module provides a simple in-memory registry for revoked tokens to
illustrate compliance with RFC 7009. The registry can be toggled on or off
via the ``enable_rfc7009`` setting in ``runtime_cfg.Settings``.
"""

from __future__ import annotations

from typing import Set

from .runtime_cfg import settings

# In-memory set storing revoked tokens for demonstration and testing purposes
_REVOKED_TOKENS: Set[str] = set()


def revoke_token(token: str) -> None:
    """Revoke *token* by adding it to the registry.

    No-op if ``settings.enable_rfc7009`` is ``False``.
    """
    if not settings.enable_rfc7009:
        return
    _REVOKED_TOKENS.add(token)


def is_revoked(token: str) -> bool:
    """Return ``True`` if *token* has been revoked.

    Always ``False`` when RFC 7009 is disabled.
    """
    if not settings.enable_rfc7009:
        return False
    return token in _REVOKED_TOKENS


def reset_revocations() -> None:
    """Clear the revocation registry. Intended for test setup/teardown."""
    _REVOKED_TOKENS.clear()
