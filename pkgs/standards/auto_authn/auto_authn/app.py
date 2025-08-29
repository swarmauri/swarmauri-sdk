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
* System diagnostics endpoints (healthz, methodz, hookz, planz)
"""

from __future__ import annotations

import fastapi

from .routers.surface import surface_api
from .runtime_cfg import settings
from .rfc8414 import include_rfc8414
from .oidc_discovery import include_oidc_discovery
from .rfc8693 import include_rfc8693
from .rfc7591 import include_rfc7591
from .oidc_userinfo import include_oidc_userinfo
from .rfc7009 import include_rfc7009


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
surface_api.mount_jsonrpc(prefix="/rpc")
surface_api.attach_diagnostics(prefix="/system")
app.include_router(surface_api.router)  # /authn/<model> resources & flows
if settings.enable_rfc8693:
    include_rfc8693(app)
if settings.enable_rfc7591:
    include_rfc7591(app)
include_oidc_userinfo(app)
if settings.enable_rfc7009:
    include_rfc7009(app)
if settings.enable_rfc8414:
    include_rfc8414(app)
    include_oidc_discovery(app)


async def _startup() -> None:
    # 1 – metadata validation / SQLite convenience mode
    # When running on SQLite, attach the same file under the "authn" alias
    # so schema-qualified tables like "authn.tenants" work.
    await surface_api.initialize_async(sqlite_attachments={"authn": "./authn.db"})


app.add_event_handler("startup", _startup)
