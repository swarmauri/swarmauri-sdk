"""OpenID Connect discovery endpoints.

Provides `.well-known/openid-configuration` and JWKS publication for the
Tigrbl AuthN service. These features are OIDC-specific and therefore live in
an `oidc_*` module rather than an `rfcXXXX` module.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from .deps import APIRouter, FastAPI

from .rfc.rfc8414_metadata import ISSUER, JWKS_PATH
from .runtime_cfg import settings

router = APIRouter()


# ---------------------------------------------------------------------------
# Discovery document helpers
# ---------------------------------------------------------------------------
def _settings_signature() -> str:
    """Return a stable JSON signature of current settings."""
    return json.dumps(settings.model_dump(), sort_keys=True)


def _build_openid_config() -> dict[str, Any]:
    scopes = ["openid", "profile", "email", "address", "phone"]
    claims = ["sub", "name", "email", "address", "phone_number"]
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
    if settings.enable_id_token_encryption:
        config["id_token_encryption_alg_values_supported"] = ["dir"]
        config["id_token_encryption_enc_values_supported"] = ["A256GCM"]
    if settings.enable_rfc7591:
        config["registration_endpoint"] = f"{ISSUER}/register"
    if settings.enable_rfc7009:
        config["revocation_endpoint"] = f"{ISSUER}/revoked_tokens/revoke"
        config["revocation_endpoint_auth_methods_supported"] = [
            "client_secret_basic",
            "client_secret_post",
        ]
    if settings.enable_rfc7662:
        config["introspection_endpoint"] = f"{ISSUER}/introspect"
        config["introspection_endpoint_auth_methods_supported"] = [
            "client_secret_basic",
            "client_secret_post",
        ]
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
@router.get("/.well-known/openid-configuration", tags=[".well-known"])
async def openid_configuration():
    """Return OpenID Connect discovery metadata."""
    return _cached_openid_config(_settings_signature())


@router.get(JWKS_PATH, tags=[".well-known"])
async def jwks():
    """Publish all public keys in RFC 7517 JWKS format."""
    from .oidc_id_token import ensure_rsa_jwt_key, rsa_key_provider
    from .crypto import _ensure_key as ensure_ed25519_key, _provider as ed25519_provider

    await ensure_rsa_jwt_key()
    await ensure_ed25519_key()
    rsa = await rsa_key_provider().jwks()
    ed = await ed25519_provider().jwks()
    combined = {k.get("kid"): k for k in [*rsa.get("keys", []), *ed.get("keys", [])]}
    return {"keys": list(combined.values())}


# ---------------------------------------------------------------------------
# FastAPI integration
# ---------------------------------------------------------------------------


def include_oidc_discovery(app: FastAPI) -> None:
    """Attach OIDC discovery routes to *app* if not already present."""
    if not any(
        route.path == "/.well-known/openid-configuration" for route in app.routes
    ):
        app.include_router(router)


__all__ = [
    "router",
    "JWKS_PATH",
    "ISSUER",
    "include_oidc_discovery",
    "refresh_discovery_cache",
]
