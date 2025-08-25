"""Token issuance endpoint."""

from __future__ import annotations

import base64
import secrets
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...backends import AuthError
from ...fastapi_deps import get_async_db
from ...orm.tables import Client, User
from ...rfc8707 import extract_resource
from ...rfc6749 import RFC6749Error
from ...rfc6749 import (
    enforce_grant_type,
    enforce_password_grant,
    is_enabled as rfc6749_enabled,
)
from ...rfc7636_pkce import verify_code_challenge
from ...rfc8628 import DEVICE_CODES, DeviceGrantForm
from ...oidc_id_token import mint_id_token, oidc_hash
from ...rfc8414_metadata import ISSUER

from .common import (
    AuthorizationCodeGrantForm,
    PasswordGrantForm,
    TokenPair,
    _ALLOWED_GRANT_TYPES,
    _jwt,
    _pwd_backend,
    _require_tls,
    AUTH_CODES,
)

router = APIRouter()


@router.post("/token", response_model=TokenPair)
async def token(
    request: Request, db: AsyncSession = Depends(get_async_db)
) -> TokenPair:
    _require_tls(request)
    form = await request.form()
    resources = form.getlist("resource")
    data = dict(form)
    data.pop("resource", None)
    # Client authentication (RFC 6749 §2.3)
    auth = request.headers.get("Authorization")
    client_id = None
    client_secret = None
    if auth and auth.startswith("Basic "):
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

    try:
        grant_type = enforce_grant_type(data, _ALLOWED_GRANT_TYPES)
    except RFC6749Error as exc:
        return JSONResponse(
            {"error": exc.error}, status_code=status.HTTP_400_BAD_REQUEST
        )

    aud: Optional[str] = None
    if resources:
        try:
            aud = extract_resource(resources)
        except ValueError:
            return JSONResponse(
                {"error": "invalid_target"}, status_code=status.HTTP_400_BAD_REQUEST
            )

    if grant_type == "password":
        try:
            parsed = PasswordGrantForm(**data)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())
        try:
            enforce_password_grant(parsed.username, parsed.password)
            user = await _pwd_backend.authenticate(db, parsed.username, parsed.password)
        except (AuthError, RFC6749Error) as exc:  # type: ignore[name-defined]
            return JSONResponse(
                {"error": getattr(exc, "error", "access_denied")},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        jwt_kwargs = {"aud": aud} if aud else {}
        access, refresh = await _jwt.async_sign_pair(
            sub=str(user.id), tid=str(user.tenant_id), **jwt_kwargs
        )
        return TokenPair(access_token=access, refresh_token=refresh)
    if grant_type == "authorization_code":
        try:
            parsed = AuthorizationCodeGrantForm(**data)
        except ValidationError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())
        record = AUTH_CODES.get(parsed.code)
        if not record or record["client_id"] != parsed.client_id:
            return JSONResponse(
                {"error": "invalid_grant"}, status_code=status.HTTP_400_BAD_REQUEST
            )
        if datetime.utcnow() > record["expires_at"]:
            AUTH_CODES.pop(parsed.code, None)
            return JSONResponse(
                {"error": "invalid_grant"}, status_code=status.HTTP_400_BAD_REQUEST
            )
        if record.get("redirect_uri") != parsed.redirect_uri:
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
