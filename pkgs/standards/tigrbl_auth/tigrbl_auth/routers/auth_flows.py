from __future__ import annotations


import secrets

from tigrbl_auth.deps import AsyncSession, Depends, HTTPException, JSONResponse, Request
from ..db import get_db
from ..orm import AuthSession, User
from ..routers.schemas import CredsIn, TokenPair
from ..rfc.rfc8414_metadata import ISSUER
from ..oidc_id_token import mint_id_token
from ..routers.shared import _jwt, _require_tls
from .authz import router as router

api = router


@router.post("/login", response_model=TokenPair)
async def login(
    creds: CredsIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _require_tls(request)
    users = await User.handlers.list.core(
        {"payload": {"filters": {"username": creds.identifier}}, "db": db}
    )
    user = users[0] if users else None
    if user is None or not user.verify_password(creds.password):
        raise HTTPException(status_code=400, detail="invalid credentials")
    payload = {
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
    }
    session = await AuthSession.handlers.create.core({"payload": payload, "db": db})
    await db.commit()
    access, refresh = await _jwt.async_sign_pair(
        sub=str(session.user_id),
        tid=str(session.tenant_id),
        scope="openid profile email",
    )
    id_token = await mint_id_token(
        sub=str(session.user_id),
        aud=ISSUER,
        nonce=secrets.token_urlsafe(8),
        issuer=ISSUER,
        sid=str(session.id),
    )
    pair = {
        "access_token": access,
        "refresh_token": refresh,
        "id_token": id_token,
    }
    response = JSONResponse(pair)
    response.set_cookie("sid", str(session.id), httponly=True, samesite="lax")
    return response


__all__ = ["router", "api"]
