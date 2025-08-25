from __future__ import annotations

import secrets
from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from autoapi.v2.error import IntegrityError

from ...crypto import hash_pw
from ...oidc_discovery import ISSUER
from ...oidc_id_token import mint_id_token
from ...orm.tables import Tenant, User
from ...fastapi_deps import get_async_db
from .common import SESSIONS, TokenPair, _jwt, _require_tls, router


_username = constr(strip_whitespace=True, min_length=3, max_length=80)
_password = constr(min_length=8, max_length=256)


class RegisterIn(BaseModel):
    tenant_slug: constr(strip_whitespace=True, min_length=3, max_length=120)
    username: _username
    email: EmailStr
    password: _password


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

    access, refresh = await _jwt.async_sign_pair(
        sub=str(user.id), tid=str(tenant.id), scope="openid profile email"
    )
    session_id = secrets.token_urlsafe(16)
    SESSIONS[session_id] = {
        "sub": str(user.id),
        "tid": str(tenant.id),
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
