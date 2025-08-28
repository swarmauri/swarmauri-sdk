from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..backends import AuthError
from ..fastapi_deps import get_async_db
from ..oidc_id_token import mint_id_token
from ..orm.auth_session import AuthSession
from ..routers.schemas import CredsIn, TokenPair
from ..rfc8414_metadata import ISSUER
from .authz import router as router
from .shared import _jwt, _pwd_backend, AUTH_CODES, SESSIONS


@router.post("/login", response_model=TokenPair)
async def login(
    creds: CredsIn,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        user = await _pwd_backend.authenticate(db, creds.identifier, creds.password)
    except AuthError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invalid credentials")
    session_id = secrets.token_urlsafe(16)
    payload = {
        "id": session_id,
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
    }
    session = await AuthSession.handlers.create.core({"db": db, "payload": payload})
    access, refresh = await _jwt.async_sign_pair(
        sub=str(user.id), tid=str(user.tenant_id), scope="openid profile email"
    )
    SESSIONS[session.id] = {
        "sub": str(user.id),
        "tid": str(user.tenant_id),
        "username": user.username,
        "auth_time": session.auth_time,
    }
    id_token = await mint_id_token(
        sub=str(user.id),
        aud=ISSUER,
        nonce=secrets.token_urlsafe(8),
        issuer=ISSUER,
        sid=session.id,
    )
    pair = {"access_token": access, "refresh_token": refresh, "id_token": id_token}
    response = JSONResponse(pair)
    response.set_cookie("sid", session.id, httponly=True, samesite="lax")
    return response


__all__ = ["router", "_jwt", "_pwd_backend", "AUTH_CODES", "SESSIONS"]
