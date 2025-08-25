"""
autoapi_authn.routers.auth_flows
================================

Public-facing credential endpoints:

    • POST /register
    • POST /login
    • POST /token          (OAuth2 password grant)
    • POST /logout
    • POST /token/refresh
    • POST /apikeys/introspect

Notes
-----
* CRUD for tenants / clients / users / api_keys is already provided by
  AutoAPI under `/authn/<resource>` and is **not** re-implemented here.
* All endpoints are JSON; schemas are strict (Pydantic).
* `logout` is implemented as a no-op stub — token revocation / key
  deactivation should be wired to your datastore or cache later.
"""

from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, constr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..crypto import hash_pw
from ..jwtoken import JWTCoder
from ..backends import PasswordBackend, ApiKeyBackend, AuthError
from ..fastapi_deps import get_async_db
from ..orm.tables import Tenant, User
from ..typing import StrUUID
from autoapi.v2.error import IntegrityError

router = APIRouter()

_jwt = JWTCoder.default()
_pwd_backend = PasswordBackend()
_api_backend = ApiKeyBackend()

# ============================================================================
#  Helper Pydantic models
# ============================================================================
_username = constr(strip_whitespace=True, min_length=3, max_length=80)
_password = constr(min_length=8, max_length=256)


class RegisterIn(BaseModel):
    tenant_slug: constr(strip_whitespace=True, min_length=3, max_length=120)
    username: _username
    email: EmailStr
    password: _password


class CredsIn(BaseModel):
    identifier: constr(strip_whitespace=True, min_length=3, max_length=120)
    password: _password


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")


class RefreshIn(BaseModel):
    refresh_token: str


class ApiKeyIn(BaseModel):
    api_key: str


class IntrospectOut(BaseModel):
    sub: StrUUID
    tid: StrUUID
    kind: str


# ============================================================================
#  Endpoint implementations
# ============================================================================
@router.post(
    "/register",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "invalid params"},
        404: {"description": "tenant not found"},
        409: {"description": "duplicate key"},
        500: {"description": "database error"},
    },
)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_async_db)):
    try:
        # 1. look up pre-existing tenant
        tenant = await db.scalar(
            select(Tenant).where(Tenant.slug == body.tenant_slug).limit(1)
        )
        if tenant is None:
            # 404 → JSON-RPC -32601 (“method / object not found”)
            raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")

        # 2. create user
        user = User(
            tenant_id=tenant.id,
            username=body.username,
            email=body.email,
            password_hash=hash_pw(body.password),
        )
        db.add(user)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "duplicate key") from exc
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "database error"
        ) from exc

    access, refresh = _jwt.sign_pair(sub=str(user.id), tid=str(tenant.id))
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPair)
async def login(body: CredsIn, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await _pwd_backend.authenticate(db, body.identifier, body.password)
    except AuthError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid credentials")

    access, refresh = _jwt.sign_pair(sub=str(user.id), tid=str(user.tenant_id))
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/token", response_model=TokenPair)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
) -> TokenPair:
    try:
        user = await _pwd_backend.authenticate(
            db, form_data.username, form_data.password
        )
    except AuthError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid credentials")

    access, refresh = _jwt.sign_pair(sub=str(user.id), tid=str(user.tenant_id))
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    """
    Stub endpoint for client symmetry.

    *For a real implementation add token blacklist /
    API-key deactivation logic here.*
    """
    ...


@router.post("/token/refresh", response_model=TokenPair)
async def refresh(body: RefreshIn):
    try:
        access, refresh = _jwt.refresh(body.refresh_token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
    return TokenPair(access_token=access, refresh_token=refresh)


# --------------------------------------------------------------------------
#  API-key introspection – **does not** clash with /authn/api_keys CRUD
# --------------------------------------------------------------------------
@router.post("/api_key/introspect", response_model=IntrospectOut)
async def introspect_key(body: ApiKeyIn, db: AsyncSession = Depends(get_async_db)):
    try:
        principal, kind = await _api_backend.authenticate(db, body.api_key)
    except AuthError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, exc.reason)

    return IntrospectOut(sub=str(principal.id), tid=str(principal.tenant_id), kind=kind)
