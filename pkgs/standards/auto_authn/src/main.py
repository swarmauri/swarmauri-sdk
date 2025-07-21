"""
auth_authn_idp.main
===================
ASGI entry‑point for the Auth‑AuthN Identity‑Provider.

Run locally
-----------
    uvicorn auth_authn_idp.main:app --reload

Or with explicit host/port:

    AUTH_AUTHN_PUBLIC_URL=https://login.localhost \
    uvicorn auth_authn_idp.main:app --host 0.0.0.0 --port 8443
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .db import lifespan
from .middlewares import rate_limit_middleware  # optional; comment if unused
from .provider import router as oidc_router

log = logging.getLogger("auth_authn.main")

###############################################################################
# FastAPI application                                                         #
###############################################################################

app = FastAPI(
    title="Auth‑AuthN Identity‑Provider",
    version=settings.project_name + "-" + settings.environment,
    lifespan=lifespan,
    docs_url="/docs",               # swagger‑ui
    redoc_url=None,
    openapi_url="/openapi.json",
)

# --------------------------------------------------------------------------- #
# Middleware                                                                  #
# --------------------------------------------------------------------------- #
# 1.  CORS (for browser‑based RPs)
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.cors_origins],  # HttpUrl → str
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    log.info("CORS enabled for %s", settings.cors_origins)

# 2.  Global rate‑limit (optional)
app.add_middleware(rate_limit_middleware, max_per_min=settings.rate_limit_per_min)

# --------------------------------------------------------------------------- #
# Routers                                                                     #
# --------------------------------------------------------------------------- #
app.include_router(oidc_router)

# Health‑check † (Kubernetes readinessProbe)
@app.get("/healthz", tags=["infra"])
async def health() -> JSONResponse:  # pragma: no cover
    return JSONResponse({"status": "ok"})


# Root landing page
@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:  # pragma: no cover
    return JSONResponse(
        {
            "service": "Auth‑AuthN IdP",
            "environment": settings.environment,
            "version": settings.project_name,
            "tenants_discovery": "/<tenant>/.well-known/openid-configuration",
        }
    )

###############################################################################
# Optional module‑level entry‑point                                           #
###############################################################################
if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "auth_authn_idp.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
