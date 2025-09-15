from __future__ import annotations


import secrets

from tigrbl_auth.deps import (
    AsyncSession,
    Depends,
    Request,
    HTTPException,
    select,
    status,
    JSONResponse,
)

from ..fastapi_deps import get_db
from ..orm.auth_session import AuthSession
from ..orm.user import User
from ..oidc_id_token import mint_id_token
from ..routers.schemas import CredsIn, TokenPair
from ..routers.shared import _jwt, _require_tls
from ..rfc.rfc8414_metadata import ISSUER
from .authz import router as router

api = router


@router.post("/login", response_model=TokenPair)
async def login(
    creds: CredsIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.username == creds.identifier)
    user = await db.scalar(stmt)
    if user is None or not user.verify_password(creds.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid credentials"
        )

    _require_tls(request)
    payload = {
        "username": user.username,
        "user_id": user.id,
        "tenant_id": user.tenant_id,
    }
    session = await AuthSession.handlers.create.core({"db": db, "payload": payload})
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
