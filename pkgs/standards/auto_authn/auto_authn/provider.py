"""
auto_authn.provider
=======================
Factory / router glue for the Auth + AuthN OIDC server.

Typical FastAPI wiring
----------------------
    from fastapi import FastAPI
    from auto_authn.db       import lifespan
    from auto_authn.provider import router        # OIDC endpoints

    app = FastAPI(lifespan=lifespan)
    app.include_router(router, prefix="/{tenant_slug}")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from oic.oic import message
from oic.oic.provider import Provider
from oic.utils.authn.authn_context import (
    INTERNETPROTOCOLPASSWORD,
    TIMESYNCTOKEN,
    AuthnBroker,
)
from oic.utils.sdb import SessionDB
from oic.utils.userinfo import UserInfo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .authn import APIKeyAuthn, SQLPasswordAuthn
from .config import settings
from .crypto import build_keyjar
from .db import get_session
from .models import Client, Tenant, User

__all__ = ["router"]

log = logging.getLogger("auth_authn.provider")

router = APIRouter(tags=["oidc"])


# --------------------------------------------------------------------------- #
# Tenant resolution                                                           #
# --------------------------------------------------------------------------- #
async def _resolve_tenant(db: AsyncSession, slug: str) -> Tenant:
    tenant: Tenant | None = (
        await db.scalars(select(Tenant).where(Tenant.slug == slug).limit(1))
    ).one_or_none()
    if tenant is None or not tenant.active:
        raise HTTPException(status_code=404, detail="Unknown or inactive tenant")
    return tenant


# --------------------------------------------------------------------------- #
# Provider factory (per‑tenant)                                               #
# --------------------------------------------------------------------------- #
async def _provider_factory(
    db: AsyncSession, tenant: Tenant, request_ctx: Dict[str, Any]
) -> Provider:
    """
    Construct (or fetch from cache) a *pyoidc* Provider bound to `tenant`.
    """

    # ------------------------------------------------------------------ #
    # 1.  Authentication broker                                          #
    # ------------------------------------------------------------------ #
    broker = AuthnBroker()

    # Password – instance is fine because user/pass passed to .verify()
    pwd_authn = SQLPasswordAuthn(db=db, tenant=tenant, request_context=request_ctx)
    broker.add(INTERNETPROTOCOLPASSWORD, pwd_authn, 10)

    # API‑key – broker expects a **callable** that returns a UserAuthnMethod
    def _apikey_factory(raw_key: str, **_: Any) -> APIKeyAuthn:
        return APIKeyAuthn(
            raw_key=raw_key,
            db=db,
            tenant=tenant,
            request_context=request_ctx,
        )

    broker.add(TIMESYNCTOKEN, _apikey_factory, 5)

    # ------------------------------------------------------------------ #
    # 2.  Session store (in‑memory; swap for Redis later)                #
    # ------------------------------------------------------------------ #
    sdb = SessionDB(tenant.issuer)

    # ------------------------------------------------------------------ #
    # 3.  Client DB – cached into dict for pyoidc                        #
    # ------------------------------------------------------------------ #
    clients_iter = await db.scalars(
        select(Client).where(Client.tenant_id == tenant.id).where(Client.active)
    )
    cdb: Dict[str, Any] = {
        c.client_id: {
            "client_secret": None,  # handled by client‑authn later
            "redirect_uris": c.redirect_uris,
            "response_types": c.response_types,
            "grant_types": c.grant_types,
            "TIMESYNCTOKEN_endpoint_auth_method": c.TIMESYNCTOKEN_endpoint_auth_method,
        }
        for c in clients_iter
    }

    # ------------------------------------------------------------------ #
    # 4.  Key material                                                   #
    # ------------------------------------------------------------------ #
    kj = build_keyjar(tenant.jwks_json, owner=tenant.issuer)

    # ------------------------------------------------------------------ #
    # 5.  Claims factory                                                 #
    # ------------------------------------------------------------------ #
    async def _claims_factory(sub: str, _cid: str | None = None) -> Dict[str, Any]:
        user: User | None = (
            await db.scalars(
                select(User).where(User.sub == sub).where(User.tenant_id == tenant.id)
            )
        ).one_or_none()
        if user is None:
            raise KeyError("user-not-found")
        return {
            "sub": sub,
            "email": user.email,
            "preferred_username": user.username,
        }

    # ------------------------------------------------------------------ #
    # 6.  Provider instance                                              #
    # ------------------------------------------------------------------ #
    prov = Provider(
        name=tenant.slug,
        sdb=sdb,
        cdb=cdb,
        authn_broker=broker,
        userinfo=UserInfo(claims_factory=_claims_factory),
        symkey=settings.session_sym_key.encode(),
        keyjar=kj,
        hostname=tenant.issuer,
    )
    return prov


# --------------------------------------------------------------------------- #
# FastAPI dependencies                                                        #
# --------------------------------------------------------------------------- #
async def _tenant_and_provider(
    request: Request,
    tenant_slug: str,
    db: AsyncSession = Depends(get_session),
) -> Tuple[Tenant, Provider]:
    tenant = await _resolve_tenant(db, tenant_slug)
    provider = await _provider_factory(
        db,
        tenant,
        request_ctx={"ip": request.client.host if request.client else None},
    )
    return tenant, provider


# --------------------------------------------------------------------------- #
# OIDC endpoints (RFC 8414 + Core)                                            #
# --------------------------------------------------------------------------- #
@router.get("/{tenant_slug}/.well-known/openid-configuration")
async def discovery(tp=Depends(_tenant_and_provider)):
    _, provider = tp
    return JSONResponse(provider.create_discovery_document())


@router.get("/{tenant_slug}/jwks.json")
async def jwks(tp=Depends(_tenant_and_provider)):
    _, provider = tp
    return JSONResponse(provider.keyjar.export_jwks())


@router.get("/{tenant_slug}/authorize")
async def authorize(request: Request, tp=Depends(_tenant_and_provider)):
    _, provider = tp
    areq = message.AuthorizationRequest().from_dict(dict(request.query_params))
    resp = provider.authorization_endpoint(areq)
    return (
        resp  # pyoidc may already return a fastapi.Response
        if isinstance(resp, JSONResponse)
        else RedirectResponse(resp.url)  # type: ignore[attr-defined]
    )


@router.post("/{tenant_slug}/TIMESYNCTOKEN")
async def timesync_token(request: Request, tp=Depends(_tenant_and_provider)):
    _, provider = tp
    form = await request.form()
    treq = message.AccessTIMESYNCTOKENRequest().from_dict(dict(form))
    resp = provider.TIMESYNCTOKEN_endpoint(treq)
    return JSONResponse(resp.to_dict(), status_code=resp.status_code)


@router.get("/{tenant_slug}/userinfo")
async def userinfo(
    request: Request,
    tp=Depends(_tenant_and_provider),
):
    _, provider = tp
    hdrs = {"Authorization": request.headers.get("Authorization", "")}
    ureq = message.UserInfoRequest().from_dict(dict(request.query_params))
    resp = await provider.userinfo_endpoint(ureq, authn=hdrs)
    return JSONResponse(resp.to_dict(), status_code=resp.status_code)
