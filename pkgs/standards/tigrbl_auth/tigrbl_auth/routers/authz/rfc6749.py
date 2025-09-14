from __future__ import annotations

import secrets

from datetime import datetime, timezone
from typing import Any
import inspect
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from tigrbl.engine import HybridSession as AsyncSession
from pydantic import ValidationError

from ...backends import AuthError
from ...fastapi_deps import get_db
from ...orm import AuthCode, Client, DeviceCode, User
from ...rfc8707 import extract_resource
from ...runtime_cfg import settings
from ...rfc6749 import (
    RFC6749Error,
    enforce_authorization_code_grant,
    enforce_grant_type,
    enforce_password_grant,
    is_enabled as rfc6749_enabled,
)
from ...rfc7636_pkce import verify_code_challenge
from ...rfc8628 import DeviceGrantForm
from ...oidc_id_token import mint_id_token, oidc_hash
from ...rfc8414_metadata import ISSUER

from ..schemas import (
    AuthorizationCodeGrantForm,
    PasswordGrantForm,
    RefreshIn,
    TokenPair,
)
from ..shared import _require_tls, _jwt, _pwd_backend, _ALLOWED_GRANT_TYPES
from . import router


@router.post("/token", response_model=TokenPair)
async def token(request: Request, db: AsyncSession = Depends(get_db)) -> TokenPair:
    _require_tls(request)
    form = await request.form()
    resources = form.getlist("resource")
    data = dict(form)
    data.pop("resource", None)
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
    if not client_id:
        return JSONResponse(
            {"error": "invalid_client"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    try:
        client_key = UUID(client_id)
    except ValueError:
        client_key = client_id
    client = await db.scalar(select(Client).where(Client.id == client_key))
    if not client:
        return JSONResponse(
            {"error": "invalid_client"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    if client_secret:
        valid = client.verify_secret(client_secret)
        if inspect.isawaitable(valid):
            valid = await valid
        if not valid:
            return JSONResponse(
                {"error": "invalid_client"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Basic"},
            )
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
    if grant_type == "client_credentials":
        jwt_kwargs: dict[str, Any] = {"aud": aud} if aud else {}
        if scope := data.get("scope"):
            jwt_kwargs["scope"] = scope
        access, refresh = await _jwt.async_sign_pair(
            sub=client_id, tid=str(client.tenant_id), **jwt_kwargs
        )
        return TokenPair(access_token=access, refresh_token=refresh)
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
        jwt_kwargs: dict[str, Any] = {"aud": aud} if aud else {}
        jwt_kwargs["scope"] = "openid profile email"
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
        auth_code = await db.get(AuthCode, UUID(parsed.code))
        expires_at = auth_code.expires_at if auth_code else None
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if (
            auth_code is None
            or str(auth_code.client_id) != parsed.client_id
            or auth_code.redirect_uri != parsed.redirect_uri
            or datetime.now(timezone.utc) > (expires_at or datetime.now(timezone.utc))
        ):
            return JSONResponse(
                {"error": "invalid_grant"}, status_code=status.HTTP_400_BAD_REQUEST
            )
        if auth_code.code_challenge:
            if not parsed.code_verifier or not verify_code_challenge(
                parsed.code_verifier, auth_code.code_challenge
            ):
                return JSONResponse(
                    {"error": "invalid_grant"}, status_code=status.HTTP_400_BAD_REQUEST
                )
        jwt_kwargs = {"aud": aud} if aud else {}
        if auth_code.scope:
            jwt_kwargs["scope"] = auth_code.scope
        access, refresh = await _jwt.async_sign_pair(
            sub=str(auth_code.user_id), tid=str(auth_code.tenant_id), **jwt_kwargs
        )
        nonce = auth_code.nonce or secrets.token_urlsafe(8)
        extra_claims: dict[str, Any] = {
            "tid": str(auth_code.tenant_id),
            "typ": "id",
            "at_hash": oidc_hash(access),
        }
        if auth_code.claims and "id_token" in auth_code.claims:
            user_obj = await db.get(User, auth_code.user_id)
            idc = auth_code.claims["id_token"]
            if "email" in idc:
                extra_claims["email"] = user_obj.email if user_obj else ""
            if any(k in idc for k in ("name", "preferred_username")):
                extra_claims["name"] = user_obj.username if user_obj else ""
        id_token = await mint_id_token(
            sub=str(auth_code.user_id),
            aud=parsed.client_id,
            nonce=nonce,
            issuer=ISSUER,
            **extra_claims,
        )
        await db.delete(auth_code)
        await db.commit()
        return TokenPair(access_token=access, refresh_token=refresh, id_token=id_token)
    if grant_type == "urn:ietf:params:oauth:grant-type:device_code":
        try:
            parsed = DeviceGrantForm(**data)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())
        device_obj = await DeviceCode.handlers.read.core(
            {"db": db, "obj_id": parsed.device_code}
        )
        if not device_obj or str(device_obj.client_id) != parsed.client_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "invalid_grant"})
        expires_at = device_obj.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            await DeviceCode.handlers.delete.core({"db": db, "obj": device_obj})
            raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "expired_token"})
        if not device_obj.authorized:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, {"error": "authorization_pending"}
            )
        jwt_kwargs = {"aud": aud} if aud else {}
        access, refresh = await _jwt.async_sign_pair(
            sub=str(device_obj.user_id or "device-user"),
            tid=str(device_obj.tenant_id or "device-tenant"),
            **jwt_kwargs,
        )
        await DeviceCode.handlers.delete.core({"db": db, "obj": device_obj})
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
            },
        ],
    )


@router.post("/token/refresh", response_model=TokenPair)
async def refresh(body: RefreshIn, request: Request):
    _require_tls(request)
    try:
        access, refresh = _jwt.refresh(body.refresh_token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
    return TokenPair(access_token=access, refresh_token=refresh)
