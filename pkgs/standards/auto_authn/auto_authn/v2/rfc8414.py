"""Authorization Server Metadata support (RFC 8414).

This module provides a minimal implementation of the OAuth 2.0 Authorization
Server Metadata specification as defined in RFC 8414. When enabled via
``settings.enable_rfc8414`` it exposes a discovery document at
``/.well-known/oauth-authorization-server``.

See RFC 8414: https://www.rfc-editor.org/rfc/rfc8414
"""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter, FastAPI, HTTPException, status

from .runtime_cfg import settings
from .oidc_discovery import (
    _cached_openid_config,
    _settings_signature,
    refresh_discovery_cache,
)

RFC8414_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8414"

router = APIRouter()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.get("/.well-known/oauth-authorization-server", include_in_schema=False)
async def authorization_server_metadata():
    """Return OAuth 2.0 Authorization Server Metadata per RFC 8414."""
    if not settings.enable_rfc8414:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"RFC 8414 disabled: {RFC8414_SPEC_URL}"
        )
    return _cached_openid_config(_settings_signature())


def include_rfc8414(app: FastAPI) -> None:
    """Attach discovery routes to *app* if enabled."""
    if settings.enable_rfc8414 and not any(
        route.path == "/.well-known/oauth-authorization-server" for route in app.routes
    ):
        app.include_router(router)


__all__ = [
    "router",
    "include_rfc8414",
    "RFC8414_SPEC_URL",
    "refresh_discovery_cache",
]
