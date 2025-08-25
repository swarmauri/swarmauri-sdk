"""Credential and token flow endpoints.

This router exposes the core credential flow endpoints:

* ``POST /register``
* ``POST /login``
* ``POST /token`` (OAuth2 password grant)
* ``POST /logout``
* ``POST /token/refresh``
* ``POST /introspect``

Additional OAuth 2.0 features such as device authorization, pushed
authorization requests and token revocation are provided in dedicated modules
and can be attached to the application conditionally.

Notes
-----
* CRUD for tenants / clients / users / api_keys is already provided by
  AutoAPI under ``/authn/<resource>`` and is **not** re-implemented here.
* All endpoints are JSON; schemas are strict (Pydantic).
* ``logout`` is implemented as a no-op stub — token revocation / key
  deactivation should be wired to your datastore or cache later.
"""

from __future__ import annotations


from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, ValidationError, constr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..crypto import hash_pw
from ..jwtoken import JWTCoder
from ..backends import PasswordBackend, ApiKeyBackend, AuthError
from ..fastapi_deps import get_async_db
from ..orm.tables import Tenant, User
from ..runtime_cfg import settings
from ..typing import StrUUID
from ..rfc8707 import extract_resource
from ..rfc7009 import revoke_token
from ..rfc6749 import RFC6749Error
from ..rfc9126 import store_par_request, DEFAULT_PAR_EXPIRY
from ..rfc6749 import (
    enforce_grant_type,
    enforce_password_grant,
    is_enabled as rfc6749_enabled,
)
from ..rfc8628 import DEVICE_CODES, DeviceGrantForm
from autoapi.v2.error import IntegrityError

router = APIRouter()

_jwt = JWTCoder.default()
_pwd_backend = PasswordBackend()
_api_backend = ApiKeyBackend()

_ALLOWED_GRANT_TYPES = {"password"}
if settings.enable_rfc8628:
    _ALLOWED_GRANT_TYPES.add("urn:ietf:params:oauth:grant-type:device_code")

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


class IntrospectOut(BaseModel):
    active: bool
    sub: Optional[StrUUID] = None
    tid: Optional[StrUUID] = None
    kind: Optional[str] = None


class PasswordGrantForm(BaseModel):
    grant_type: Literal["password"]
    username: str
    password: str


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

    access, refresh = await _jwt.async_sign_pair(sub=str(user.id), tid=str(tenant.id))
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPair)
async def login(body: CredsIn, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await _pwd_backend.authenticate(db, body.identifier, body.password)
    except AuthError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid credentials")

    access, refresh = await _jwt.async_sign_pair(
        sub=str(user.id), tid=str(user.tenant_id)
    )
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/token", response_model=TokenPair)
async def token(
    request: Request, db: AsyncSession = Depends(get_async_db)
) -> TokenPair:
    form = await request.form()
    resources = form.getlist("resource")
    data = dict(form)
    data.pop("resource", None)
    grant_type = data.get("grant_type")
    aud = None
    try:
        enforce_grant_type(grant_type, _ALLOWED_GRANT_TYPES)
    except RFC6749Error as exc:
        return JSONResponse(
            {"error": str(exc)}, status_code=status.HTTP_400_BAD_REQUEST
        )
    if settings.rfc8707_enabled:
        try:
            aud = extract_resource(resources)
        except ValueError:
            return JSONResponse(
                {"error": "invalid_target"}, status_code=status.HTTP_400_BAD_REQUEST
            )
    if grant_type == "password":
        try:
            enforce_password_grant(data)
        except RFC6749Error as exc:
            return JSONResponse(
                {"error": str(exc)}, status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            parsed = PasswordGrantForm(**data)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())
        try:
            user = await _pwd_backend.authenticate(db, parsed.username, parsed.password)
        except AuthError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid credentials")
        jwt_kwargs = {"aud": aud} if aud else {}
        access, refresh = await _jwt.async_sign_pair(
            sub=str(user.id), tid=str(user.tenant_id), **jwt_kwargs
        )
        return TokenPair(access_token=access, refresh_token=refresh)
    if grant_type == "urn:ietf:params:oauth:grant-type:device_code":
        try:
            parsed = DeviceGrantForm(**data)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())
        record = DEVICE_CODES.get(parsed.device_code)
        if not record or record["client_id"] != parsed.client_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_grant"})
        if datetime.utcnow() > record["expires_at"]:
            DEVICE_CODES.pop(parsed.device_code, None)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "expired_token"})
        if not record.get("authorized"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, {"error": "authorization_pending"}
            )
        jwt_kwargs = {"aud": aud} if aud else {}
        access, refresh = await _jwt.async_sign_pair(
            sub=record.get("sub", "device-user"),
            tid=record.get("tid", "device-tenant"),
            **jwt_kwargs,
        )
        DEVICE_CODES.pop(parsed.device_code, None)
        return TokenPair(access_token=access, refresh_token=refresh)
    if rfc6749_enabled():
        return JSONResponse(
            {"error": "unsupported_grant_type"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    raise HTTPException(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        [
            {
                "loc": ["body", "grant_type"],
                "msg": "unsupported grant_type",
                "type": "value_error",
            }
        ],
    )


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
#  RFC 7662 token introspection
# --------------------------------------------------------------------------
@router.post("/introspect", response_model=IntrospectOut)
async def introspect(token: str = Form(...), db: AsyncSession = Depends(get_async_db)):
    if not settings.enable_rfc7662:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "introspection disabled")
    try:
        principal, kind = await _api_backend.authenticate(db, token)
    except AuthError:
        return IntrospectOut(active=False)
    return IntrospectOut(
        active=True,
        sub=str(principal.id),
        tid=str(principal.tenant_id),
        kind=kind,
    )
