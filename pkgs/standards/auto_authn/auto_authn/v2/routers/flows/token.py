from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...fastapi_deps import get_async_db
from ...backends import AuthError
from ...orm.tables import Client, User
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
from ...rfc8628 import DEVICE_CODES, DeviceGrantForm
from ...oidc_id_token import mint_id_token, oidc_hash
from ...rfc8414_metadata import ISSUER
from .common import (
    AUTH_CODES,
    TokenPair,
    _ALLOWED_GRANT_TYPES,
    _jwt,
    _pwd_backend,
    require_tls,
)

router = APIRouter()


class PasswordGrantForm(BaseModel):
    grant_type: str
    username: str
    password: str


class AuthorizationCodeGrantForm(BaseModel):
    grant_type: str
    code: str
    redirect_uri: str
    client_id: str
    code_verifier: Optional[str] = None


@router.post("/token", response_model=TokenPair)
async def token(
    request: Request, db: AsyncSession = Depends(get_async_db)
) -> TokenPair:
    require_tls(request)
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
        if record.get("scope"):
            jwt_kwargs["scope"] = record["scope"]
        access, refresh = await _jwt.async_sign_pair(
            sub=record["sub"], tid=record["tid"], **jwt_kwargs
        )
        nonce = record.get("nonce") or secrets.token_urlsafe(8)
        extra_claims: dict[str, Any] = {
            "tid": record["tid"],
            "typ": "id",
            "at_hash": oidc_hash(access),
        }
        if record.get("claims") and "id_token" in record["claims"]:
            from uuid import UUID

            user_obj = await db.get(User, UUID(record["sub"]))
            idc = record["claims"]["id_token"]
            if "email" in idc:
                extra_claims["email"] = user_obj.email if user_obj else ""
            if any(k in idc for k in ("name", "preferred_username")):
                extra_claims["name"] = user_obj.username if user_obj else ""
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
