"""Utilities for OAuth 2.0 Token Revocation (RFC 7009).

This module provides a simple in-memory registry for revoked tokens to
illustrate compliance with RFC 7009. The registry can be toggled on or off
via the ``enable_rfc7009`` setting in ``runtime_cfg.Settings``.

See RFC 7009: https://www.rfc-editor.org/rfc/rfc7009
"""

from __future__ import annotations

from typing import Final, Set

from fastapi import APIRouter, FastAPI, Form, HTTPException, status

from .runtime_cfg import settings

RFC7009_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7009"

# In-memory set storing revoked tokens for demonstration and testing purposes
_REVOKED_TOKENS: Set[str] = set()

router = APIRouter()


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


@router.post("/revoke")
async def revoke(token: str = Form(...), token_type_hint: str | None = Form(None)):
    """RFC 7009 token revocation endpoint."""

    if not settings.enable_rfc7009:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "revocation disabled")
    revoke_token(token)
    return {}


def include_rfc7009(app: FastAPI) -> None:
    """Attach the RFC 7009 router to *app* if enabled."""

    if settings.enable_rfc7009 and not any(
        route.path == "/revoke" for route in app.routes
    ):
        app.include_router(router)


__all__ = [
    "revoke_token",
    "is_revoked",
    "reset_revocations",
    "router",
    "include_rfc7009",
    "RFC7009_SPEC_URL",
]
