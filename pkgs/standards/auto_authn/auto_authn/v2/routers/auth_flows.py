"""
autoapi_authn.routers.auth_flows
================================

Public-facing credential endpoints:

    • POST /register
    • POST /login          (alias /token)
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
from fastapi.responses import RedirectResponse
import hashlib
import base64
import secrets
import time
from pydantic import BaseModel, EmailStr, Field, constr
from sqlalchemy.ext.asyncio import AsyncSession

from ..crypto import hash_pw
from ..jwtoken import JWTCoder
from ..backends import PasswordBackend, ApiKeyBackend, AuthError
from ..fastapi_deps import get_async_db
from ..orm.tables import Tenant, User
from ..typing import StrUUID

router = APIRouter()

_jwt = JWTCoder.default()
_pwd_backend = PasswordBackend()
_api_backend = ApiKeyBackend()

# ephemeral store for authorization codes
_codes: dict[str, dict] = {}

# ============================================================================
#  Helper Pydantic models
# ============================================================================
_username = constr(strip_whitespace=True, min_length=3, max_length=80)
_password = constr(min_length=8, max_length=256)


class RegisterIn(BaseModel):
    tenant_name: constr(strip_whitespace=True, min_length=3, max_length=120)
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


class AuthorizeIn(BaseModel):
    client_id: str
    redirect_uri: str
    code_challenge: str
    code_challenge_method: str = "S256"
    state: str | None = None
    identifier: str
    password: _password


class TokenExchange(BaseModel):
    code: str
    code_verifier: str


class IntrospectOut(BaseModel):
    sub: StrUUID
    tid: StrUUID


# ============================================================================
#  Endpoint implementations
# ============================================================================
@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_async_db)):
    # 1. create tenant
    print("here")
    tenant = Tenant(
        name=body.tenant_name, slug=body.tenant_name.lower().replace(" ", "-")
    )
    db.add(tenant)
    await db.flush()  # tenant.id available
    print("here")
    # 2. create user
    user = User(
        tenant_id=tenant.id,
        username=body.username,
        email=body.email,
        password_hash=hash_pw(body.password),
    )
    db.add(user)
    print("here")
    await db.commit()
    print("here")
    access, refresh = _jwt.sign_pair(sub=str(user.id), tid=str(tenant.id), scopes=[])
    print("now")
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPair)
@router.post("/token", include_in_schema=False)  # alias
async def login(body: CredsIn, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await _pwd_backend.authenticate(db, body.identifier, body.password)
    except AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, exc.reason)

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
@router.post("/apikeys/introspect", response_model=IntrospectOut)
async def introspect_key(body: ApiKeyIn, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await _api_backend.authenticate(db, body.api_key)
    except AuthError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, exc.reason)

    return IntrospectOut(sub=str(user.id), tid=str(user.tenant_id))


# --------------------------------------------------------------------------
#  PKCE authorization code flow
# --------------------------------------------------------------------------
@router.get("/{tenant}/authorize", include_in_schema=False)
async def authorize(
    tenant: str, q: AuthorizeIn = Depends(), db: AsyncSession = Depends(get_async_db)
):
    try:
        user = await _pwd_backend.authenticate(db, q.identifier, q.password)
    except AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, exc.reason)

    code = secrets.token_urlsafe(32)
    _codes[code] = {
        "sub": str(user.id),
        "tid": str(user.tenant_id),
        "challenge": q.code_challenge,
        "method": q.code_challenge_method,
        "exp": time.monotonic() + 600,
    }

    params = f"code={code}"
    if q.state:
        params += f"&state={q.state}"
    return RedirectResponse(url=f"{q.redirect_uri}?{params}", status_code=302)


@router.post("/{tenant}/token", response_model=TokenPair)
async def token_exchange(
    tenant: str, body: TokenExchange, db: AsyncSession = Depends(get_async_db)
):
    data = _codes.pop(body.code, None)
    if not data or time.monotonic() > data["exp"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid code")

    if data["method"].upper() == "S256":
        digest = hashlib.sha256(body.code_verifier.encode()).digest()
        verifier = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    else:
        verifier = body.code_verifier

    if verifier != data["challenge"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid code_verifier")

    access, refresh = _jwt.sign_pair(sub=data["sub"], tid=data["tid"])
    return TokenPair(access_token=access, refresh_token=refresh)
