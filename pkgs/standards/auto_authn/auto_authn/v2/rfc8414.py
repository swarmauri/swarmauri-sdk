"""Authorization Server Metadata support (RFC 8414).

This module provides a minimal implementation of the OAuth 2.0 Authorization
Server Metadata specification as defined in RFC 8414. When enabled via
``settings.enable_rfc8414`` it exposes a discovery document at
``/.well-known/oauth-authorization-server``.

See RFC 8414: https://www.rfc-editor.org/rfc/rfc8414
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Final

from fastapi import APIRouter, FastAPI, HTTPException, status

from .runtime_cfg import settings

RFC8414_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8414"

router = APIRouter()

# Default paths and issuer used for constructing metadata.
JWKS_PATH = "/.well-known/jwks.json"
ISSUER = os.getenv("AUTHN_ISSUER", "https://authn.example.com")


# ---------------------------------------------------------------------------
# Discovery document helpers
# ---------------------------------------------------------------------------
def _settings_signature() -> str:
    """Return a stable JSON signature of current settings."""
    return json.dumps(settings.model_dump(), sort_keys=True)


def _build_openid_config() -> dict[str, Any]:
    scopes = ["openid", "profile", "email", "address", "phone"]
    claims = [
        "sub",
        "name",
        "given_name",
        "family_name",
        "email",
        "email_verified",
        "address",
        "phone_number",
        "phone_number_verified",
    ]
    response_types = [
        "code",
        "token",
        "id_token",
        "code token",
        "code id_token",
        "token id_token",
        "code token id_token",
    ]
    config: dict[str, Any] = {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/authorize",
        "token_endpoint": f"{ISSUER}/token",
        "userinfo_endpoint": f"{ISSUER}/userinfo",
        "jwks_uri": f"{ISSUER}{JWKS_PATH}",
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": scopes,
        "claims_supported": claims,
        "response_types_supported": response_types,
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
        ],
        "response_modes_supported": ["query", "fragment", "form_post"],
        "code_challenge_methods_supported": ["S256"],
    }
    if settings.enable_rfc7591:
        config["registration_endpoint"] = f"{ISSUER}/register"
    if settings.enable_rfc7009:
        config["revocation_endpoint"] = f"{ISSUER}/revoke"
    if settings.enable_rfc7662:
        config["introspection_endpoint"] = f"{ISSUER}/introspect"
    return config


@lru_cache(maxsize=1)
def _cached_openid_config(sig: str) -> dict[str, Any]:
    return _build_openid_config()


def refresh_discovery_cache() -> None:
    """Clear cached discovery metadata."""
    _cached_openid_config.cache_clear()


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


@router.get("/.well-known/openid-configuration", include_in_schema=False)
async def openid_configuration():
    """Return OpenID Connect discovery metadata."""
    return _cached_openid_config(_settings_signature())


@router.get(JWKS_PATH, include_in_schema=False)
async def jwks():
    """Publish all public keys in RFC 7517 JWKS format."""
    from .oidc_id_token import ensure_rsa_jwt_key, rsa_key_provider
    from .crypto import _ensure_key as ensure_ed25519_key, _provider as ed25519_provider

    await ensure_rsa_jwt_key()
    await ensure_ed25519_key()
    rsa = await rsa_key_provider().jwks()
    ed = await ed25519_provider().jwks()
    return {"keys": [*rsa.get("keys", []), *ed.get("keys", [])]}


def include_rfc8414(app: FastAPI) -> None:
    """Attach discovery routes to *app* if enabled."""
    if settings.enable_rfc8414 and not any(
        route.path == "/.well-known/openid-configuration" for route in app.routes
    ):
        app.include_router(router)


__all__ = [
    "router",
    "JWKS_PATH",
    "ISSUER",
    "include_rfc8414",
    "RFC8414_SPEC_URL",
    "refresh_discovery_cache",
]
