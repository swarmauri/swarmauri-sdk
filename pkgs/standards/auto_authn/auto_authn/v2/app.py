"""
autoapi_authn.app
=================

FastAPI application factory for the **autoapi-authn** service.

Features
--------
* Async SQLAlchemy engine (SQLite or Postgres driven by `DATABASE_URL`)
* Auto-generated CRUD router for Tenant / Client / User / ApiKey
* Public credential routes  (/register, /login, /logout, …)
* OIDC discovery (`/.well-known/openid-configuration`) + `jwks.json`
* Health & methodz endpoints for ops
"""

from __future__ import annotations

import os
import sys

import fastapi

from autoapi.v2 import get_schema  # convenience helper for /methodz
from .routers.auth_flows import router as flows_router
from .routers.crud import crud_api as crud_api
from .runtime_cfg import settings
from .rfc8414 import include_rfc8414
from .rfc8628 import include_rfc8628
from .rfc9126 import include_rfc9126
from .rfc7009 import include_rfc7009
from .rfc8693 import include_rfc8693


# --------------------------------------------------------------------
# FastAPI application
# --------------------------------------------------------------------
app = fastapi.FastAPI(
    title="AutoAPI-AuthN",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
)

# Mount routers
app.include_router(crud_api.router)  # /authn/<model> CRUD (AutoAPI)
app.include_router(flows_router)  # /register, /login, etc.
if settings.enable_rfc8628:
    include_rfc8628(app)
if settings.enable_rfc9126:
    include_rfc9126(app)
if settings.enable_rfc7009:
    include_rfc7009(app)
if settings.enable_rfc8693:
    include_rfc8693(app)
if settings.enable_rfc8414:
    include_rfc8414(app)


# --------------------------------------------------------------------
# Operational endpoints
# --------------------------------------------------------------------
@app.get("/healthz", include_in_schema=False)
async def health_check():
    return {"status": "alive"}


@app.get("/methodz", include_in_schema=False)
async def methodz():
    """
    Basic service metadata; returns OpenAPI schema size & build info.
    """
    schema = get_schema.get_autoapi_schema(app)
    return {
        "service": app.title,
        "version": app.version,
        "routes": len(app.routes),
        "openapi_bytes": len(schema.json().encode()),
        "python": sys.version.split()[0],
    }


# --------------------------------------------------------------------
# OIDC discovery + JWKS
# --------------------------------------------------------------------
JWKS_PATH = "/.well-known/jwks.json"
ISSUER = os.getenv("AUTHN_ISSUER", "https://authn.example.com")  # adjust in prod


@app.get("/.well-known/openid-configuration", include_in_schema=False)
async def oidc_config():
    return {
        "issuer": ISSUER,
        "jwks_uri": f"{ISSUER}{JWKS_PATH}",
        "token_endpoint": f"{ISSUER}/token",
        "registration_endpoint": f"{ISSUER}/register",
        "scopes_supported": ["openid", "profile", "email", "address", "phone"],
        "claims_supported": [
            "sub",
            "name",
            "given_name",
            "family_name",
            "email",
            "email_verified",
            "address",
            "phone_number",
            "phone_number_verified",
        ],
        "response_types_supported": ["token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["EdDSA"],
    }


@app.get(JWKS_PATH, include_in_schema=False)
async def jwks():
    """
    Return Ed25519 public key in RFC 7517 JWK Set format.
    """
    from .crypto import _provider, _ensure_key

    kid, _, _ = await _ensure_key()
    kp = _provider()
    key_dict = await kp.get_public_jwk(kid)
    key_dict.setdefault("kid", f"{kid}.1")
    return {"keys": [key_dict]}


async def _startup() -> None:
    # 1 – metadata validation / SQLite convenience mode
    await crud_api.initialize_async()


app.add_event_handler("startup", _startup)
