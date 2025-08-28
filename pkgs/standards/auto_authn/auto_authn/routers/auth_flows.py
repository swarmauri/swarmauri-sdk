from __future__ import annotations

import asyncio
import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_async_db
from ..orm.auth_session import AuthSession
from ..oidc_id_token import mint_id_token
from ..rfc8414_metadata import ISSUER
from .authz import router as authz_router
from .shared import _jwt, _pwd_backend, _require_tls, AUTH_CODES, SESSIONS


router = APIRouter()
router.include_router(authz_router)


class LoginPayload(BaseModel):
    """Credentials for username/password login."""

    identifier: str
    password: str


@router.post("/login")
async def login(
    payload: LoginPayload,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """Authenticate a user and mint an authorization session."""

    #_require_tls(request)
    user = await _pwd_backend.authenticate(db, payload.identifier, payload.password)
    session_id = secrets.token_urlsafe(16)
    session = await AuthSession.handlers.create.core(
        {
            "db": db,
            "payload": {
                "id": session_id,
                "user_id": user.id,
                "tenant_id": user.tenant_id,
                "username": user.username,
            },
        }
    )
    access, refresh = await _jwt.async_sign_pair(
        sub=str(user.id),
        tid=str(user.tenant_id),
        scope="openid profile email",
    )
    SESSIONS[session.id] = {
        "sub": str(user.id),
        "tid": str(user.tenant_id),
        "username": user.username,
        "auth_time": session.auth_time,
    }
    id_token = await asyncio.to_thread(
        mint_id_token,
        sub=str(user.id),
        aud=ISSUER,
        nonce=secrets.token_urlsafe(8),
        issuer=ISSUER,
        sid=session.id,
    )
    pair = {
        "access_token": access,
        "refresh_token": refresh,
        "id_token": id_token,
    }
    response = JSONResponse(pair)
    response.set_cookie("sid", session.id, httponly=True, samesite="lax")
    return response


__all__ = ["router", "_jwt", "_pwd_backend", "AUTH_CODES", "SESSIONS"]
