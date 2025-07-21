"""
auth_authn_idp.middleware
=========================
Common FastAPI authentication helpers.

Components
----------
* **AuthMiddleware** – inspects every request, validates credentials, and
  attaches `request.state.principal`.
* **Principal**      – lightweight container describing the caller.
* **get_principal**  – dependency that returns the principal or raises *401*.

Supported credentials
---------------------
1. **Bearer JWT**  (issued by this IdP, validated against the tenant JWKS)
2. **API Key**     (header `X‑API‑Key` **or** `Authorization: ApiKey <secret>`)

Assumptions
-----------
• All tenant‑scoped routes start with `/{tenant_slug}/…`.
• Your FastAPI app already wires the database `lifespan()` from
  `auth_authn_idp.db`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, Request
from jose import JWTError, jwk, jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .api_keys import verify_api_key
from .config import settings
from .db import SessionMaker
from .models import Tenant

# --------------------------------------------------------------------------- #
# Typed principal object                                                      #
# --------------------------------------------------------------------------- #


@dataclass(slots=True)
class Principal:
    sub: str
    tenant_id: int
    scopes: set[str]
    auth_method: str  # "bearer" | "api_key"
    api_key_id: Optional[str] = None  # UUID str when method == api_key


# --------------------------------------------------------------------------- #
# Middleware                                                                  #
# --------------------------------------------------------------------------- #


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Populates `request.state.principal` if credentials verify successfully.

    Does **not** reject anonymous requests; that is handled by `get_principal`.
    """

    _TENANT_RE = re.compile(r"^/([^/]+)/")

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # --------------------------------------------------------------- #
        # 1. Resolve tenant slug (bypass if not tenant‑scoped)            #
        # --------------------------------------------------------------- #
        match = self._TENANT_RE.match(request.url.path)
        if not match:  # e.g., /health or /
            return await call_next(request)

        tenant_slug = match.group(1)

        async with SessionMaker() as db:  # type: ignore[arg-type]
            tenant = await _get_active_tenant(db, tenant_slug)
            if tenant:
                principal = await _authenticate(request, tenant, db)
                request.state.principal = principal  # may be None

        return await call_next(request)


# --------------------------------------------------------------------------- #
# FastAPI dependency                                                          #
# --------------------------------------------------------------------------- #


async def get_principal(request: Request) -> Principal:
    """
    Dependency for protected routes.

        @router.get("/me")
        async def whoami(principal: Principal = Depends(get_principal)):
            return {"sub": principal.sub}
    """
    principal: Principal | None = getattr(request.state, "principal", None)
    if principal is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return principal


# --------------------------------------------------------------------------- #
# Internal helpers                                                            #
# --------------------------------------------------------------------------- #


async def _get_active_tenant(db: AsyncSession, slug: str) -> Tenant | None:
    from .models import Tenant

    return (
        await db.scalars(select(Tenant).where(Tenant.slug == slug).where(Tenant.active))
    ).one_or_none()


async def _authenticate(
    request: Request, tenant: Tenant, db: AsyncSession
) -> Principal | None:
    """
    Try API‑key first (CI / automation), then Bearer JWT.
    """
    # ---------------------------- #
    # API‑Key                      #
    # ---------------------------- #
    api_key = request.headers.get("X-API-Key") or _extract_prefixed(
        request.headers.get("Authorization"), "ApiKey"
    )
    if api_key:
        rec = await verify_api_key(api_key, db, tenant.id)
        if rec and rec.is_active():
            return Principal(
                sub=rec.owner_id,  # owner_id contains User.id (int) here
                tenant_id=tenant.id,
                scopes=set(rec.scopes),
                auth_method="api_key",
                api_key_id=str(rec.id),
            )

    # ---------------------------- #
    # Bearer JWT                   #
    # ---------------------------- #
    bearer = _extract_prefixed(request.headers.get("Authorization"), "Bearer")
    if bearer:
        try:
            claims = _decode_jwt(bearer, tenant)
            scopes = set(claims.get("scope", "").split())
            return Principal(
                sub=claims["sub"],
                tenant_id=tenant.id,
                scopes=scopes,
                auth_method="bearer",
            )
        except JWTError:
            pass  # fallthrough to anonymous

    # Anonymous
    return None


def _extract_prefixed(value: str | None, prefix: str) -> str | None:
    if not value:
        return None
    scheme, _, rest = value.partition(" ")
    return rest if scheme.lower() == prefix.lower() else None


def _decode_jwt(token: str, tenant: Tenant) -> dict:
    """
    Minimal JWT verification using python‑jose and the tenant's JWKS.
    Audience / issuer validation is **optional** – enable if you enforce them.
    """
    jwks = json.loads(tenant.jwks_json)
    hdr = jwt.get_unverified_header(token)
    kid = hdr.get("kid")
    jwk_obj = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if jwk_obj is None:
        raise JWTError("kid-not-found")

    key = jwk.construct(jwk_obj)
    return jwt.decode(
        token,
        key.to_pem().decode() if hasattr(key, "to_pem") else key.key,
        algorithms=[jwk_obj["alg"]],
        issuer=tenant.issuer,
        audience=settings.jwt_audience,
        options={"verify_aud": bool(settings.jwt_audience)},
    )
