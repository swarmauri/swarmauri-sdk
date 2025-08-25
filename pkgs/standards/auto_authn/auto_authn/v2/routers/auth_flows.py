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


import secrets
from datetime import datetime, timedelta
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, Field, ValidationError, constr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode
from uuid import UUID

from ..crypto import hash_pw
from ..jwtoken import JWTCoder
from ..backends import PasswordBackend, ApiKeyBackend, AuthError
from ..fastapi_deps import get_async_db
from ..orm.tables import Tenant, User, Client
from ..runtime_cfg import settings
from ..typing import StrUUID
from ..rfc8707 import extract_resource
from ..rfc6749 import RFC6749Error
from ..rfc6749 import (
    enforce_authorization_code_grant,
    enforce_grant_type,
    enforce_password_grant,
    is_enabled as rfc6749_enabled,
)
from ..rfc7636_pkce import verify_code_challenge
from ..rfc8628 import DEVICE_CODES, DeviceGrantForm
from autoapi.v2.error import IntegrityError
from ..oidc_id_token import mint_id_token, oidc_hash, verify_id_token
from ..rfc8414 import ISSUER
from ..rfc8252 import is_native_redirect_uri

router = APIRouter()

_jwt = JWTCoder.default()
_pwd_backend = PasswordBackend()
_api_backend = ApiKeyBackend()

_ALLOWED_GRANT_TYPES = {"password", "authorization_code"}
if settings.enable_rfc8628:
    _ALLOWED_GRANT_TYPES.add("urn:ietf:params:oauth:grant-type:device_code")

AUTH_CODES: dict[str, dict] = {}
SESSIONS: dict[str, dict] = {}


def _require_tls(request: Request) -> None:
    if settings.require_tls and request.url.scheme != "https":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "tls_required"})


async def _front_channel_logout(session_id: str) -> None:
    """Placeholder for front-channel logout notifications."""
    return None


async def _back_channel_logout(session_id: str) -> None:
    """Placeholder for back-channel logout notifications."""
    return None


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
    id_token: Optional[str] = None


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    id_token_hint: str


class IntrospectOut(BaseModel):
    active: bool
    sub: Optional[StrUUID] = None
    tid: Optional[StrUUID] = None
    kind: Optional[str] = None


class PasswordGrantForm(BaseModel):
    grant_type: Literal["password"]
    username: str
    password: str


class AuthorizationCodeGrantForm(BaseModel):
    grant_type: Literal["authorization_code"]
    code: str
    redirect_uri: str
    client_id: str
    code_verifier: Optional[str] = None


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
async def register(
    body: RegisterIn, request: Request, db: AsyncSession = Depends(get_async_db)
):
    _require_tls(request)
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
    session_id = secrets.token_urlsafe(16)
    SESSIONS[session_id] = {"sub": str(user.id), "tid": str(tenant.id)}
    id_token = mint_id_token(
        sub=str(user.id),
        aud=ISSUER,
        nonce=secrets.token_urlsafe(8),
        issuer=ISSUER,
        sid=session_id,
    )
    pair = TokenPair(access_token=access, refresh_token=refresh, id_token=id_token)
    response = JSONResponse(pair.model_dump())
    response.set_cookie("sid", session_id, httponly=True, samesite="lax")
    return response


@router.post("/login", response_model=TokenPair)
async def login(
    body: CredsIn, request: Request, db: AsyncSession = Depends(get_async_db)
):
    _require_tls(request)
    try:
        user = await _pwd_backend.authenticate(db, body.identifier, body.password)
    except AuthError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid credentials")

    access, refresh = await _jwt.async_sign_pair(
        sub=str(user.id), tid=str(user.tenant_id)
    )
    session_id = secrets.token_urlsafe(16)
    SESSIONS[session_id] = {"sub": str(user.id), "tid": str(user.tenant_id)}
    id_token = mint_id_token(
        sub=str(user.id),
        aud=ISSUER,
        nonce=secrets.token_urlsafe(8),
        issuer=ISSUER,
        sid=session_id,
    )
    pair = TokenPair(access_token=access, refresh_token=refresh, id_token=id_token)
    response = JSONResponse(pair.model_dump())
    response.set_cookie("sid", session_id, httponly=True, samesite="lax")
    return response


@router.get("/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    request: Request,
    response_mode: Optional[str] = None,
    state: Optional[str] = None,
    nonce: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    _require_tls(request)
    rts = set(response_type.split())
    allowed = {"code", "token", "id_token"}
    if not rts or not rts.issubset(allowed):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, {"error": "unsupported_response_type"}
        )
    scopes = set(scope.split())
    if "openid" not in scopes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_scope"})
    if "id_token" in rts and not nonce:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    try:
        client_uuid = UUID(client_id)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    client = await db.get(Client, client_uuid)
    if client is None or redirect_uri not in (client.redirect_uris or "").split():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    if username is None or password is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, {"error": "access_denied"})
    try:
        user = await _pwd_backend.authenticate(db, username, password)
    except AuthError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, {"error": "access_denied"})
    if is_native_redirect_uri(redirect_uri) and not code_challenge:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    if code_challenge_method and code_challenge_method != "S256":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_request"})
    mode = response_mode or "query"
    if mode not in {"query", "fragment", "form_post"}:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, {"error": "unsupported_response_mode"}
        )
    params: list[tuple[str, str]] = []
    code: str | None = None
    access: str | None = None
    if "code" in rts:
        code = secrets.token_urlsafe(32)
        AUTH_CODES[code] = {
            "sub": str(user.id),
            "tid": str(user.tenant_id),
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code_challenge": code_challenge,
            "nonce": nonce,
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
        }
        params.append(("code", code))
    if "token" in rts:
        access = await _jwt.async_sign(sub=str(user.id), tid=str(user.tenant_id))
        params.append(("access_token", access))
        params.append(("token_type", "bearer"))
    if "id_token" in rts:
        from ..rfc8414 import ISSUER

        extra_claims: dict[str, str] = {
            "tid": str(user.tenant_id),
            "typ": "id",
        }
        if access:
            extra_claims["at_hash"] = oidc_hash(access)
        if code:
            extra_claims["c_hash"] = oidc_hash(code)
        id_token = mint_id_token(
            sub=str(user.id),
            aud=client_id,
            nonce=nonce,
            issuer=ISSUER,
            **extra_claims,
        )
        params.append(("id_token", id_token))
    if state:
        params.append(("state", state))
    if mode == "fragment":
        redirect_url = f"{redirect_uri}#{urlencode(params)}" if params else redirect_uri
        return RedirectResponse(redirect_url)
    if mode == "form_post":
        inputs = "".join(
            f'<input type="hidden" name="{k}" value="{v}" />' for k, v in params
        )
        body = (
            "<!DOCTYPE html><html><body>"
            f'<form method="post" action="{redirect_uri}">{inputs}</form>'
            "<script>document.forms[0].submit()</script>"
            "</body></html>"
        )
        return HTMLResponse(content=body)
    redirect_url = f"{redirect_uri}?{urlencode(params)}" if params else redirect_uri
    return RedirectResponse(redirect_url)


@router.post("/token", response_model=TokenPair)
async def token(
    request: Request, db: AsyncSession = Depends(get_async_db)
) -> TokenPair:
    _require_tls(request)
    form = await request.form()
    resources = form.getlist("resource")
    data = dict(form)
    data.pop("resource", None)
    # ------------------------------------------------------------------
    # Client authentication (RFC 6749 §2.3)
    # ------------------------------------------------------------------
    auth = request.headers.get("Authorization")
    client_id = None
    client_secret = None
    if auth and auth.startswith("Basic "):
        import base64

        try:
            decoded = base64.b64decode(auth.split()[1]).decode()
            client_id, client_secret = decoded.split(":", 1)
        except Exception:
            return JSONResponse(
                {"error": "invalid_client"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Basic"},
            )
    else:
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")
    if not client_id or not client_secret:
        return JSONResponse(
            {"error": "invalid_client"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    client = await db.scalar(select(Client).where(Client.id == client_id))
    if not client or not client.verify_secret(client_secret):
        return JSONResponse(
            {"error": "invalid_client"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    # Ensure form client_id matches authenticated client when provided
    if data.get("client_id") and data["client_id"] != client_id:
        return JSONResponse(
            {"error": "invalid_client"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    data["client_id"] = client_id
    data.pop("client_secret", None)
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
    if grant_type == "authorization_code":
        try:
            enforce_authorization_code_grant(data)
        except RFC6749Error as exc:
            return JSONResponse(
                {"error": str(exc)}, status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            parsed = AuthorizationCodeGrantForm(**data)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())
        record = AUTH_CODES.pop(parsed.code, None)
        if (
            record is None
            or record["client_id"] != parsed.client_id
            or record["redirect_uri"] != parsed.redirect_uri
            or datetime.utcnow() > record["expires_at"]
        ):
            return JSONResponse(
                {"error": "invalid_grant"}, status_code=status.HTTP_400_BAD_REQUEST
            )
        if record.get("code_challenge"):
            if not parsed.code_verifier or not verify_code_challenge(
                parsed.code_verifier, record["code_challenge"]
            ):
                return JSONResponse(
                    {"error": "invalid_grant"}, status_code=status.HTTP_400_BAD_REQUEST
                )
        jwt_kwargs = {"aud": aud} if aud else {}
        access, refresh = await _jwt.async_sign_pair(
            sub=record["sub"], tid=record["tid"], **jwt_kwargs
        )
        nonce = record.get("nonce") or secrets.token_urlsafe(8)
        extra_claims = {
            "tid": record["tid"],
            "typ": "id",
            "at_hash": oidc_hash(access),
        }
        id_token = mint_id_token(
            sub=record["sub"],
            aud=parsed.client_id,
            nonce=nonce,
            issuer=ISSUER,
            **extra_claims,
        )
        return TokenPair(access_token=access, refresh_token=refresh, id_token=id_token)
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
async def logout(body: LogoutIn, request: Request):
    _require_tls(request)
    """RP-initiated logout endpoint.

    Validates the ``id_token_hint`` and clears the session cookie. This is a
    minimal reference implementation; integrate with your datastore or cache
    for production use.
    """
    try:
        claims = verify_id_token(body.id_token_hint, issuer=ISSUER, audience=ISSUER)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "invalid id_token_hint"
        ) from exc
    sid = claims.get("sid")
    if sid:
        SESSIONS.pop(sid, None)
        await _front_channel_logout(sid)
        await _back_channel_logout(sid)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("sid")
    return response


@router.post("/token/refresh", response_model=TokenPair)
async def refresh(body: RefreshIn, request: Request):
    _require_tls(request)
    try:
        access, refresh = _jwt.refresh(body.refresh_token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
    return TokenPair(access_token=access, refresh_token=refresh)


# --------------------------------------------------------------------------
#  RFC 7662 token introspection
# --------------------------------------------------------------------------
@router.post("/introspect", response_model=IntrospectOut)
async def introspect(request: Request, db: AsyncSession = Depends(get_async_db)):
    _require_tls(request)
    if not settings.enable_rfc7662:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "introspection disabled")
    form = await request.form()
    token = form.get("token")
    if not token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "token parameter required")
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
