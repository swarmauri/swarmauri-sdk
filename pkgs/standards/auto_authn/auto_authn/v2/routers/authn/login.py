from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...oidc_id_token import mint_id_token
from ...rfc8414_metadata import ISSUER
from ...fastapi_deps import get_async_db
from ...orm.tables import AuthSession

from ..schemas import CredsIn, TokenPair
from ..shared import _require_tls, _jwt, SESSIONS

from . import router


@router.post("/login", response_model=TokenPair)
async def login(
    body: CredsIn, request: Request, db: AsyncSession = Depends(get_async_db)
):
    _require_tls(request)
    session_id = secrets.token_urlsafe(16)
    try:
        session = await AuthSession.handlers.login.core(
            {
                "db": db,
                "payload": {
                    "id": session_id,
                    "username": body.identifier,
                    "password": body.password,
                },
            }
        )
    except HTTPException:
        raise

    access, refresh = await _jwt.async_sign_pair(
        sub=str(session.user_id),
        tid=str(session.tenant_id),
        scope="openid profile email",
    )
    SESSIONS[session.id] = {
        "sub": str(session.user_id),
        "tid": str(session.tenant_id),
        "username": session.username,
        "auth_time": session.auth_time,
    }
    id_token = mint_id_token(
        sub=str(session.user_id),
        aud=ISSUER,
        nonce=secrets.token_urlsafe(8),
        issuer=ISSUER,
        sid=session.id,
    )
    pair = TokenPair(access_token=access, refresh_token=refresh, id_token=id_token)
    response = JSONResponse(pair.model_dump())
    response.set_cookie("sid", session.id, httponly=True, samesite="lax")
    return response
