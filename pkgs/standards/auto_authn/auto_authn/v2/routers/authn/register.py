from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...oidc_id_token import mint_id_token
from ...rfc8414_metadata import ISSUER
from ...orm.tables import AuthSession, Tenant, User
from ...fastapi_deps import get_async_db

from ..schemas import RegisterIn, TokenPair
from ..shared import _require_tls, _jwt, SESSIONS

from . import router


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
        tenant = await db.scalar(
            select(Tenant).where(Tenant.slug == body.tenant_slug).limit(1)
        )
        if tenant is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "tenant not found")
        await User.handlers.register.core(
            {
                "db": db,
                "payload": {
                    "tenant_id": tenant.id,
                    "username": body.username,
                    "email": body.email,
                    "password": body.password,
                },
            }
        )
        session_id = secrets.token_urlsafe(16)
        session = await AuthSession.handlers.login.core(
            {
                "db": db,
                "payload": {
                    "id": session_id,
                    "username": body.username,
                    "password": body.password,
                },
            }
        )
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        from autoapi.v2.error import IntegrityError

        if isinstance(exc, IntegrityError):
            raise HTTPException(status.HTTP_409_CONFLICT, "duplicate key") from exc
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "database error"
        ) from exc

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
