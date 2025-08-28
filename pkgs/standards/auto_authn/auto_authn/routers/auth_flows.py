from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..fastapi_deps import get_async_db
from sqlalchemy import select

from ..orm.tables import AuthSession, User
from .authz import router as router
from .shared import AUTH_CODES, SESSIONS, _require_tls


class LoginRequest(BaseModel):
    identifier: str
    password: str


@router.post("/login")
async def login(
    credentials: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    _require_tls(request)
    user = await db.scalar(
        select(User).where(User.username == credentials.identifier).limit(1)
    )
    if user is None or not user.verify_password(credentials.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid credentials")

    session_id = secrets.token_urlsafe(16)
    session = await AuthSession.handlers.create.core(
        {
            "db": db,
            "payload": {
                "id": session_id,
                "tenant_id": user.tenant_id,
                "user_id": user.id,
                "username": user.username,
            },
        }
    )
    SESSIONS[session.id] = {
        "sub": str(user.id),
        "tid": str(user.tenant_id),
        "username": user.username,
        "auth_time": session.auth_time,
    }
    response = JSONResponse({"sid": session.id})
    response.set_cookie("sid", session.id, httponly=True, samesite="lax")
    return response


__all__ = ["router", "AUTH_CODES", "SESSIONS"]
