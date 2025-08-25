from __future__ import annotations

from typing import Optional, Dict

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, Field

from ...jwtoken import JWTCoder
from ...backends import PasswordBackend
from ...runtime_cfg import settings

_jwt = JWTCoder.default()
_pwd_backend = PasswordBackend()

_ALLOWED_GRANT_TYPES = {"password", "authorization_code"}
if settings.enable_rfc8628:
    _ALLOWED_GRANT_TYPES.add("urn:ietf:params:oauth:grant-type:device_code")

AUTH_CODES: Dict[str, Dict] = {}
SESSIONS: Dict[str, Dict] = {}


def require_tls(request: Request) -> None:
    if settings.require_tls and request.url.scheme != "https":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "tls_required"})


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")
    id_token: Optional[str] = None
