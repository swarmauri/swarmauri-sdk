"""
auth_authn_idp.provider
=======================
Provider‑factory + HTTP router glue for the Auth + AuthN OIDC server.

Typical use
-----------
    from fastapi import FastAPI
    from auth_authn_idp.provider import router    # per‑tenant endpoints
    from auth_authn_idp.db        import lifespan

    app = FastAPI(lifespan=lifespan)
    app.include_router(router, prefix="/{tenant_slug}")

The path prefix `/tenants/{tenant_slug}` works just as well – adjust in `router`
below to suit your chosen URL style.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from oic.oic import message
from oic.oic.provider import Provider
from oic.utils.authn.authn_context import INTERNETPROTOCOLPASSWORD
from oic.utils.authn.broker import AuthnBroker
from oic.utils.sdb import SessionDB
from oic.utils.userinfo import UserInfo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .authn import SQLPasswordAuthn
from .config import settings
from .crypto import build_keyjar
from .db import get_session
from .models import Client, Tenant, User

log = logging.getLogger("auth_authn.provider")

# FastAPI router exported to main.py
router = APIRouter(tags=["oidc"])

# --------------------------------------------------------------------------- #
# Helpers for resolving tenant & building provider                            #
# --------------------------------------------------------------------------- #


async def _resolve_tenant(db: AsyncSession, slug: str) -> Tenant:
    tenant: Tenant | None = (
        await db.scalars(select(Tenant).where(Tenant.slug == slug).limit(1))
    ).one_or_none()
    if tenant is None or not tenant.active:
        raise HTTPException(status_code=404, detail="Unknown or inactive tenant")
    return tenant


async def _provider_factory(
    db: AsyncSession, tenant: Tenant, request_ctx: Optional[Dict[str, Any]] = None
) -> Provider:
    """
    Build (or fetch from cache) a pyoidc Provider bound to `tenant`.
    """
    # In production you may memoise this inside an LRU keyed by tenant.id
    # because Provider construction is reasonably cheap but not free.
    broker = AuthnBroker()
    broker.add(
        INTERNETPROTOCOLPASSWORD,
        SQLPasswordAuthn(db=db, tenant=tenant, request_context=request_ctx or {}),
        10,
    )

    # SessionDB can be backed by in‑memory dict; replace with redis later.
    session_db = SessionDB(tenant.issuer)

    # Client store – lazily populated from DB (pyoidc expects dict)
    client_rows = await db.scalars(
        select(Client).where(Client.tenant_id == tenant.id).where(Client.active)
    )
    cdb: Dict[str, Any] = {}
    for c in client_rows:
        cdb[c.client_id] = {
            "client_secret": c.client_secret_hash,  # handled by authn method
            "redirect_uris": c.redirect_uris,
            "response_types": c.response_types,
            "grant_types": c.grant_types,
            "token_endpoint_auth_method": c.token_endpoint_auth_method,
        }

    # KeyJar contains *both* public & private halves
    kj = build_keyjar(tenant.jwks_json, owner=tenant.issuer)

    async def _claims_factory(
        sub: str, _client_id: str | None = None
    ) -> Dict[str, Any]:
        user: User | None = (
            await db.scalars(
                select(User).where(User.sub == sub).where(User.tenant_id == tenant.id)
            )
        ).one_or_none()
        if user is None:
            raise KeyError("user-not-found")
        return {"sub": sub, "email": user.email, "preferred_username": user.username}

    prov = Provider(
        name=tenant.issuer,
        sdb=session_db,
        cdb=cdb,
        authn_broker=broker,
        userinfo=UserInfo(claims_factory=_claims_factory),
        symkey=settings.session_sym_key.encode(),
        keyjar=kj,
        hostname=tenant.issuer,  # ensures links use correct host
    )

    return prov


# --------------------------------------------------------------------------- #
# FastAPI dependencies                                                        #
# --------------------------------------------------------------------------- #


async def get_tenant_and_provider(
    request: Request,
    tenant_slug: str,
    db: AsyncSession = Depends(get_session),
):
    """
    Common dependency used by all OIDC endpoints.
    """
    tenant = await _resolve_tenant(db, tenant_slug)
    provider = await _provider_factory(
        db,
        tenant,
        request_ctx={"ip": request.client.host if request.client else None},
    )
    return tenant, provider


# --------------------------------------------------------------------------- #
# Endpoint implementations                                                    #
# --------------------------------------------------------------------------- #


@router.get("/{tenant_slug}/.well-known/openid-configuration")
async def discovery(
    tp=Depends(get_tenant_and_provider),
):
    tenant, provider = tp
    return JSONResponse(provider.create_discovery_document())


@router.get("/{tenant_slug}/jwks.json")
async def jwks(tp=Depends(get_tenant_and_provider)):
    tenant, provider = tp
    return JSONResponse({"keys": provider.keyjar.export_jwks().get("keys", [])})


@router.get("/{tenant_slug}/authorize")
async def authorize(request: Request, tp=Depends(get_tenant_and_provider)):
    tenant, provider = tp
    areq = message.AuthorizationRequest().from_dict(dict(request.query_params))
    log.debug("AuthZ request tenant=%s %s", tenant.slug, areq.to_dict())
    resp = provider.authorization_endpoint(areq)
    # pyoidc returns either a message or Redirect. Both have .request() or .url
    if isinstance(resp, Response):
        return resp
    return RedirectResponse(resp.url)  # type: ignore[attr-defined]


@router.post("/{tenant_slug}/token")
async def token(request: Request, tp=Depends(get_tenant_and_provider)):
    tenant, provider = tp
    form = await request.form()
    treq = message.AccessTokenRequest().from_dict(dict(form))
    resp = provider.token_endpoint(treq)
    return JSONResponse(resp.to_dict(), status_code=resp.status_code)


@router.get("/{tenant_slug}/userinfo")
async def userinfo(
    request: Request,
    tp=Depends(get_tenant_and_provider),
    db: AsyncSession = Depends(get_session),
):
    tenant, provider = tp
    # pyoidc userinfo endpoint expects dict of query params + headers
    headers = {"Authorization": request.headers.get("Authorization", "")}
    ureq = message.UserInfoRequest().from_dict(dict(request.query_params))
    resp = await provider.userinfo_endpoint(ureq, authn=headers)
    return JSONResponse(resp.to_dict(), status_code=resp.status_code)
