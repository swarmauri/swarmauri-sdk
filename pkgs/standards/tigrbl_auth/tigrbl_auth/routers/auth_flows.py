from __future__ import annotations


from tigrbl_auth.deps import Request
from ..orm.auth_session import AuthSession
from ..routers.schemas import CredsIn, TokenPair
from .authz import router as router

api = router


@router.post("/login", response_model=TokenPair)
async def login(
    creds: CredsIn,
    request: Request,
):
    ctx = {
        "payload": {"username": creds.identifier},
        "temp": {"password": creds.password},
        "request": request,
    }
    return await AuthSession.handlers.login.core(ctx)


__all__ = ["router", "api"]
