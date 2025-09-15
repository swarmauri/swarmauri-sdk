from __future__ import annotations


from tigrbl_auth.deps import AsyncSession, Depends, Request

from ..fastapi_deps import get_db
from ..orm.auth_session import AuthSession
from ..routers.schemas import CredsIn
from .authz import router as router
from .shared import _jwt, _pwd_backend

api = router


@router.post("/login")
async def login(
    creds: CredsIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await _pwd_backend.authenticate(db, creds.identifier, creds.password)
    ctx = {
        "db": db,
        "payload": {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "username": user.username,
        },
        "request": request,
    }
    return await AuthSession.handlers.login.core(ctx)


__all__ = ["api", "router", "_jwt", "_pwd_backend"]
