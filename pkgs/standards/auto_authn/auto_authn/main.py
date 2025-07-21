"""
auto_authn.main
===================
ASGI entry‑point for the Auto‑AuthN Identity‑Provider.

Run locally
-----------
    uvicorn auto_authn.main:app --reload
"""

from __future__ import annotations

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

from .api_keys import create_api_key, revoke_api_key
from .config import settings
from .db import get_session, lifespan
from .middleware import AuthMiddleware, Principal, get_principal
from .models import APIKey
from .schema import APIKeyOut
from .provider import router as oidc_router
from pydantic import BaseModel, Field


log = logging.getLogger("auth_authn.main")

###############################################################################
# FastAPI application                                                         #
###############################################################################

app = FastAPI(
    title="Auth‑AuthN Identity‑Provider",
    version=f"{settings.project_name}-{settings.environment}",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

# --------------------------------------------------------------------------- #
# Global middleware                                                           #
# --------------------------------------------------------------------------- #
app.add_middleware(AuthMiddleware)  # populates request.state.principal

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.cors_origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    log.info("CORS enabled for %s", settings.cors_origins)

# --------------------------------------------------------------------------- #
# Routers (OIDC + API‑keys)                                                   #
# --------------------------------------------------------------------------- #
app.include_router(oidc_router)  # /{tenant_slug}/…

# ------------------------  API‑Key Management  ----------------------------- #
api_router = APIRouter(prefix="/{tenant_slug}/api-keys", tags=["api-keys"])


class IssueKey(BaseModel):
    scopes: List[str] = Field(default_factory=list)
    ttl_days: int = Field(default=30, ge=7, le=90)
    label: Optional[str] = None


@api_router.post("/", response_model=str, status_code=201)
async def issue_key(
    payload: IssueKey,
    principal: Principal = Depends(get_principal),
    tenant_slug: str = Path(..., description="Tenant slug in URL"),
    db=Depends(get_session),
):
    """
    Create a new API key for the authenticated user.
    """
    secret = await create_api_key(
        db=db,
        tenant_id=principal.tenant_id,
        owner_id=principal.sub,
        scopes=payload.scopes,
        ttl_days=payload.ttl_days,
        label=payload.label,
    )
    return secret  # show **once** to caller


@api_router.get("/", response_model=List[APIKeyOut])
async def list_keys(
    principal: Principal = Depends(get_principal),
    db=Depends(get_session),
):
    """
    List caller's API keys (metadata only, secret is never returned).
    """
    keys = await db.scalars(
        (
            select(APIKey)
            .where(APIKey.owner_id == principal.sub)
            .where(APIKey.tenant_id == principal.tenant_id)
        )
    )
    return list(keys)


@api_router.delete("/{key_id}", status_code=204)
async def revoke_key(
    key_id: UUID,
    principal: Principal = Depends(get_principal),
    db=Depends(get_session),
):
    """
    Revoke an API key owned by the caller.
    """
    success = await revoke_api_key(db, tenant_id=principal.tenant_id, api_key_id=key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found or already revoked")


app.include_router(api_router)


# --------------------------------------------------------------------------- #
# Misc endpoints                                                              #
# --------------------------------------------------------------------------- #
@app.get("/healthz", tags=["infra"])
async def health() -> JSONResponse:  # pragma: no cover
    return JSONResponse({"status": "ok"})


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:  # pragma: no cover
    return JSONResponse(
        {
            "service": "Auth‑AuthN IdP",
            "environment": settings.environment,
            "version": settings.project_name,
            "discovery": "/<tenant>/.well-known/openid-configuration",
        }
    )


###############################################################################
# Optional CLI entry‑point                                                    #
###############################################################################
if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "auto_authn.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
