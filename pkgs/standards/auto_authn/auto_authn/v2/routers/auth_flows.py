"""
autoapi_authn.routers.auth_flows
================================

Public-facing credential endpoints:

    • POST /register
    • POST /login
    • POST /token          (OAuth2 password grant)
    • POST /logout
    • POST /token/refresh
    • POST /introspect

Notes
-----
* CRUD for tenants / clients / users / api_keys is already provided by
  AutoAPI under `/authn/<resource>` and is **not** re-implemented here.
* All endpoints are JSON; schemas are strict (Pydantic).
* `logout` is implemented as a no-op stub — token revocation / key
  deactivation should be wired to your datastore or cache later.
"""

from __future__ import annotations


from datetime import datetime, timedelta
from uuid import uuid4
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
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
from ..runtime_cfg import settings
from ..rfc8707 import extract_resource
from autoapi.v2.error import IntegrityError

router = APIRouter()

_jwt = JWTCoder.default()
_pwd_backend = PasswordBackend()
_api_backend = ApiKeyBackend()

# In-memory store for device authorization data as per RFC 8628
_DEVICE_CODES: Dict[str, Dict[str, Any]] = {}
_DEVICE_VERIFICATION_URI = "https://example.com/device"
_DEVICE_CODE_EXPIRES_IN = 600  # seconds
_DEVICE_CODE_INTERVAL = 5  # seconds

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


class DeviceAuthIn(BaseModel):
    """Request body for RFC 8628 device authorization."""

    client_id: str
    scope: str | None = None


class DeviceAuthOut(BaseModel):
    """Response body for RFC 8628 device authorization."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class PasswordGrantForm(BaseModel):
    grant_type: Literal["password"]
    username: str
    password: str


class DeviceGrantForm(BaseModel):
    grant_type: Literal["urn:ietf:params:oauth:grant-type:device_code"]
    device_code: str
    client_id: str


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


@router.post("/device_authorization", response_model=DeviceAuthOut)
async def device_authorization(body: DeviceAuthIn) -> DeviceAuthOut:
    device_code = uuid4().hex
    user_code = uuid4().hex[:8]
    verification_uri = _DEVICE_VERIFICATION_URI
    verification_uri_complete = f"{verification_uri}?user_code={user_code}"
    expires_at = datetime.utcnow() + timedelta(seconds=_DEVICE_CODE_EXPIRES_IN)
    _DEVICE_CODES[device_code] = {
        "user_code": user_code,
        "client_id": body.client_id,
        "expires_at": expires_at,
        "interval": _DEVICE_CODE_INTERVAL,
        "authorized": False,
        "sub": None,
        "tid": None,
    }
    return DeviceAuthOut(
        device_code=device_code,
        user_code=user_code,
        verification_uri=verification_uri,
        verification_uri_complete=verification_uri_complete,
        expires_in=_DEVICE_CODE_EXPIRES_IN,
        interval=_DEVICE_CODE_INTERVAL,
    )


def approve_device_code(device_code: str, sub: str, tid: str) -> None:
    """Mark a device code as authorized for testing purposes."""
    if device_code in _DEVICE_CODES:
        _DEVICE_CODES[device_code]["authorized"] = True
        _DEVICE_CODES[device_code]["sub"] = sub
        _DEVICE_CODES[device_code]["tid"] = tid


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
    if settings.rfc8707_enabled:
        try:
            aud = extract_resource(resources)
        except ValueError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, {"error": "invalid_target"}
            )
    if grant_type == "password":
        try:
            parsed = PasswordGrantForm(**data)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())
        try:
            user = await _pwd_backend.authenticate(db, parsed.username, parsed.password)
        except AuthError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid credentials")
        jwt_kwargs = {"aud": aud} if aud else {}
        access, refresh = _jwt.sign_pair(
            sub=str(user.id), tid=str(user.tenant_id), **jwt_kwargs
        )
        return TokenPair(access_token=access, refresh_token=refresh)
    if grant_type == "urn:ietf:params:oauth:grant-type:device_code":
        try:
            parsed = DeviceGrantForm(**data)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())
        record = _DEVICE_CODES.get(parsed.device_code)
        if not record or record["client_id"] != parsed.client_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_grant"})
        if datetime.utcnow() > record["expires_at"]:
            _DEVICE_CODES.pop(parsed.device_code, None)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "expired_token"})
        if not record.get("authorized"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, {"error": "authorization_pending"}
            )
        jwt_kwargs = {"aud": aud} if aud else {}
        access, refresh = _jwt.sign_pair(
            sub=record.get("sub", "device-user"),
            tid=record.get("tid", "device-tenant"),
            **jwt_kwargs,
        )
        _DEVICE_CODES.pop(parsed.device_code, None)
        return TokenPair(access_token=access, refresh_token=refresh)
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
