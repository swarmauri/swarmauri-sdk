from __future__ import annotations

import secrets
from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from sqlalchemy.ext.asyncio import AsyncSession

from ...fastapi_deps import get_async_db
from ...oidc_discovery import ISSUER
from ...oidc_id_token import mint_id_token
from ...backends import AuthError
from .common import SESSIONS, TokenPair, _jwt, _pwd_backend, _require_tls, router


_username = constr(strip_whitespace=True, min_length=3, max_length=120)
_password = constr(min_length=8, max_length=256)


class CredsIn(BaseModel):
    identifier: _username
    password: _password


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
        sub=str(user.id), tid=str(user.tenant_id), scope="openid profile email"
    )
    session_id = secrets.token_urlsafe(16)
    SESSIONS[session_id] = {
        "sub": str(user.id),
        "tid": str(user.tenant_id),
        "username": user.username,
        "auth_time": datetime.utcnow(),
    }
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
