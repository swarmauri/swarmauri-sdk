"""Utilities for OAuth 2.0 Token Revocation (RFC 7009).

This module provides a simple in-memory registry for revoked tokens to
illustrate compliance with RFC 7009. The registry can be toggled on or off
via the ``enable_rfc7009`` setting in ``runtime_cfg.Settings``.

See RFC 7009: https://www.rfc-editor.org/rfc/rfc7009
"""

from __future__ import annotations

from typing import Final, Set

from tigrbl_auth.deps import TigrblApi, TigrblApp, Form, HTTPException, status

from ..runtime_cfg import settings

RFC7009_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7009"

api = TigrblApi()
router = api

# In-memory set storing revoked tokens for demonstration and testing purposes
_REVOKED_TOKENS: Set[str] = set()


def revoke_token(token: str) -> None:
    """Revoke *token* by adding it to the registry.

    No-op if ``settings.enable_rfc7009`` is ``False``.
    Also removes the token from the RFC 7662 introspection registry
    when enabled.
    """
    if not settings.enable_rfc7009:
        return
    _REVOKED_TOKENS.add(token)
    if settings.enable_rfc7662:
        from .rfc7662 import unregister_token

        unregister_token(token)


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


@api.post("/revoked_tokens/revoke")
async def revoke(token: str = Form(...)) -> dict[str, str]:
    """RFC 7009 token revocation endpoint."""
    if not settings.enable_rfc7009:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"RFC 7009 disabled: {RFC7009_SPEC_URL}"
        )
    revoke_token(token)
    return {}


def include_rfc7009(app: TigrblApp) -> None:
    """Attach revocation routes to *app* if enabled."""
    if settings.enable_rfc7009 and not any(
        route.path == "/revoked_tokens/revoke" for route in app.routes
    ):
        app.include_router(api)


__all__ = [
    "revoke_token",
    "is_revoked",
    "reset_revocations",
    "include_rfc7009",
    "api",
    "router",
    "RFC7009_SPEC_URL",
]
