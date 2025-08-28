"""Authentication flow endpoints such as /login and /logout."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_async_db
from ..orm.auth_session import AuthSession
from .authz import router as authz_router
from .shared import _jwt, _pwd_backend, AUTH_CODES, SESSIONS

router = APIRouter()
router.include_router(authz_router)


@router.post("/login")
async def login(request: Request, db: AsyncSession = Depends(get_async_db)):
    data = await request.json()
    identifier = data.get("identifier")
    password = data.get("password")
    user = await _pwd_backend.authenticate(db, identifier, password)
    session = AuthSession(
        id=secrets.token_urlsafe(16),
        username=user.username,
        user_id=user.id,
        tenant_id=user.tenant_id,
    )
    db.add(session)
    auth_time = session.auth_time
    await db.commit()
    SESSIONS[session.id] = {
        "sub": str(user.id),
        "tid": str(user.tenant_id),
        "username": user.username,
        "auth_time": auth_time,
    }
    response = JSONResponse({"status": "ok"})
    response.set_cookie("sid", session.id, httponly=True, samesite="lax")
    return response


@router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_async_db)):
    payload = await request.json()
    return await AuthSession.handlers.logout.handler(
        {"request": request, "payload": payload, "db": db}
    )


__all__ = [
    "router",
    "_jwt",
    "_pwd_backend",
    "AUTH_CODES",
    "SESSIONS",
]
