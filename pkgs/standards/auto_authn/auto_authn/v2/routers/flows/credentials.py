from __future__ import annotations

import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...crypto import hash_pw
from ...fastapi_deps import get_async_db
from ...orm.tables import Tenant, User
from ...rfc8414_metadata import ISSUER
from ...oidc_id_token import mint_id_token
from .common import (
    TokenPair,
    require_tls,
    _jwt,
    _pwd_backend,
    SESSIONS,
)

router = APIRouter()

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
    require_tls(request)
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
    except Exception as exc:
        await db.rollback()
        if isinstance(exc, HTTPException):
            raise
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


@router.post("/login", response_model=TokenPair)
async def login(
    body: CredsIn, request: Request, db: AsyncSession = Depends(get_async_db)
):
    require_tls(request)
    try:
        user = await _pwd_backend.authenticate(db, body.identifier, body.password)
    except Exception:
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
