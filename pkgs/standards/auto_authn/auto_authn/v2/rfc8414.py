"""Authorization Server Metadata support (RFC 8414).

This module provides a minimal implementation of the OAuth 2.0 Authorization
Server Metadata specification as defined in RFC 8414.  When enabled via
``settings.enable_rfc8414`` it exposes a discovery document at
``/.well-known/oauth-authorization-server``.
"""

from __future__ import annotations

import os
from fastapi import APIRouter, HTTPException, status

from .runtime_cfg import settings

router = APIRouter()

# Default paths and issuer used for constructing metadata.
JWKS_PATH = "/.well-known/jwks.json"
ISSUER = os.getenv("AUTHN_ISSUER", "https://authn.example.com")


@router.get("/.well-known/oauth-authorization-server", include_in_schema=False)
async def authorization_server_metadata():
    """Return OAuth 2.0 Authorization Server Metadata per RFC 8414."""
    if not settings.enable_rfc8414:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "RFC 8414 disabled")
    return {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/authorize",
        "token_endpoint": f"{ISSUER}/token",
        "jwks_uri": f"{ISSUER}{JWKS_PATH}",
        "scopes_supported": ["openid", "profile", "email"],
        "response_types_supported": ["code", "token"],
    }


__all__ = ["router", "JWKS_PATH", "ISSUER"]
