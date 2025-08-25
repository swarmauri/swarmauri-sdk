from __future__ import annotations

from fastapi import HTTPException, Request, Response, status

from ...oidc_id_token import verify_id_token
from ...rfc8414_metadata import ISSUER

from ..schemas import LogoutIn
from ..shared import _require_tls, _front_channel_logout, _back_channel_logout, SESSIONS

from . import router


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutIn, request: Request):
    _require_tls(request)
    try:
        claims = verify_id_token(body.id_token_hint, issuer=ISSUER, audience=ISSUER)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "invalid id_token_hint"
        ) from exc
    sid = claims.get("sid")
    if sid:
        SESSIONS.pop(sid, None)
        await _front_channel_logout(sid)
        await _back_channel_logout(sid)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("sid")
    return response
