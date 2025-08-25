"""Authorization Server Metadata support (RFC 8414).

This module provides a minimal implementation of the OAuth 2.0 Authorization
Server Metadata specification as defined in RFC 8414. When enabled via
``settings.enable_rfc8414`` it exposes a discovery document at
``/.well-known/oauth-authorization-server``.

See RFC 8414: https://www.rfc-editor.org/rfc/rfc8414
"""

from __future__ import annotations

import os
from fastapi import APIRouter, FastAPI, HTTPException, status
from typing import Final

from .runtime_cfg import settings

RFC8414_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8414"

router = APIRouter()

# Default paths and issuer used for constructing metadata.
JWKS_PATH = "/.well-known/jwks.json"
ISSUER = os.getenv("AUTHN_ISSUER", "https://authn.example.com")


@router.get("/.well-known/oauth-authorization-server", include_in_schema=False)
async def authorization_server_metadata():
    """Return OAuth 2.0 Authorization Server Metadata per RFC 8414."""
    if not settings.enable_rfc8414:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"RFC 8414 disabled: {RFC8414_SPEC_URL}"
        )
    return {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/authorize",
        "token_endpoint": f"{ISSUER}/token",
        "jwks_uri": f"{ISSUER}{JWKS_PATH}",
        "scopes_supported": ["openid", "profile", "email", "address", "phone"],
        "response_types_supported": ["code", "token"],
    }


def include_rfc8414(app: FastAPI) -> None:
    """Attach the RFC 8414 router to *app* if enabled."""
    if settings.enable_rfc8414 and not any(
        route.path == "/.well-known/oauth-authorization-server" for route in app.routes
    ):
        app.include_router(router)


__all__ = ["router", "JWKS_PATH", "ISSUER", "include_rfc8414", "RFC8414_SPEC_URL"]
