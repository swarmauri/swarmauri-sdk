from __future__ import annotations


from tigrbl_auth.deps import AsyncSession, Depends, Request

from ..fastapi_deps import get_db
from ..orm.auth_session import AuthSession
from ..routers.schemas import CredsIn, TokenPair
from .authz import router as router


@router.post("/login", response_model=TokenPair)
async def login(
    creds: CredsIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ctx = {
        "db": db,
        "payload": {"username": creds.identifier, "password": creds.password},
        "request": request,
    }
    return await AuthSession.handlers.login.core(ctx)


__all__ = ["router"]
