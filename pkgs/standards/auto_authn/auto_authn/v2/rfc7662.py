"""Utilities for OAuth 2.0 Token Introspection (RFC 7662).

This module provides a simple in-memory registry for token introspection to
illustrate compliance with RFC 7662. The registry can be toggled on or off via
the ``enable_rfc7662`` setting in ``runtime_cfg.Settings``.

See RFC 7662: https://www.rfc-editor.org/rfc/rfc7662
"""

from __future__ import annotations

from typing import Any, Dict, Final

from . import runtime_cfg

RFC7662_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7662"

# In-memory store mapping tokens to their introspection responses
_ACTIVE_TOKENS: Dict[str, Dict[str, Any]] = {}


def register_token(token: str, claims: Dict[str, Any] | None = None) -> None:
    """Register *token* as active with optional introspection *claims*."""
    data: Dict[str, Any] = {"active": True}
    if claims:
        data.update(claims)
    _ACTIVE_TOKENS[token] = data


def introspect_token(token: str) -> Dict[str, Any]:
    """Return the RFC 7662 introspection response for *token*.

    Raises
    ------
    RuntimeError
        If RFC 7662 support is disabled via settings.
    """
    if not runtime_cfg.settings.enable_rfc7662:
        raise RuntimeError(f"RFC 7662 support is disabled: {RFC7662_SPEC_URL}")
    return _ACTIVE_TOKENS.get(token, {"active": False})


def reset_tokens() -> None:
    """Clear the introspection registry. Intended for tests."""
    _ACTIVE_TOKENS.clear()


__all__ = ["register_token", "introspect_token", "reset_tokens", "RFC7662_SPEC_URL"]
