from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel

from ...oidc_id_token import verify_id_token
from ...rfc8414_metadata import ISSUER
from .common import SESSIONS, require_tls

router = APIRouter()


class LogoutIn(BaseModel):
    id_token_hint: str


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutIn, request: Request):
    require_tls(request)
    try:
        claims = verify_id_token(body.id_token_hint, issuer=ISSUER, audience=ISSUER)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "invalid id_token_hint"
        ) from exc
    sid = claims.get("sid")
    if sid:
        SESSIONS.pop(sid, None)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("sid")
    return response
