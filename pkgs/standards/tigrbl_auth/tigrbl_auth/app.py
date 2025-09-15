"""
tigrbl_auth.app
===============

FastAPI application factory for the **tigrbl-auth** service.

Features
--------
* Async SQLAlchemy engine (SQLite or Postgres driven by `DATABASE_URL`)
* Auto-generated CRUD router for Tenant / Client / User / ApiKey
* Public credential routes  (/register, /login, /logout, …)
* OIDC discovery (`/.well-known/openid-configuration`) + `jwks.json`
* System diagnostics endpoints (healthz, methodz, hookz, kernelz)
"""

from __future__ import annotations

from tigrbl_auth.deps import TigrblApp

from .routers.surface import surface_api
from .db import dsn
from .runtime_cfg import settings
from .rfc.rfc8414 import include_rfc8414
from .oidc_discovery import include_oidc_discovery
from .rfc.rfc8693 import include_rfc8693
from .oidc_userinfo import include_oidc_userinfo
from .rfc.rfc7009 import include_rfc7009


import logging

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
# --------------------------------------------------------------------
# TigrblApp application
# --------------------------------------------------------------------
app = TigrblApp(
    title="Tigrbl-Auth",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    engine=dsn,
)

# Mount routers
surface_api.mount_jsonrpc(prefix="/rpc")
surface_api.attach_diagnostics(prefix="/system")
app.include_router(surface_api)  # /authn/<model> resources & flows
if settings.enable_rfc8693:
    include_rfc8693(app)
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
    # this should work without sqlite_attachments, if sqlite_attachments are required use:
    # > await surface_api.initialize(sqlite_attachments={"authn": "./authn.db"})
    if not getattr(surface_api, "_ddl_executed", False):
        await surface_api.initialize()


app.add_event_handler("startup", _startup)
