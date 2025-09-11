from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request, status

from ..jwtoken import JWTCoder
from ..backends import PasswordBackend
from ..runtime_cfg import settings

_jwt = JWTCoder.default()
_pwd_backend = PasswordBackend()

_ALLOWED_GRANT_TYPES = {"password", "authorization_code"}
if settings.enable_rfc8628:
    _ALLOWED_GRANT_TYPES.add("urn:ietf:params:oauth:grant-type:device_code")

AUTH_CODES: dict[str, dict[str, Any]] = {}
SESSIONS: dict[str, dict[str, Any]] = {}


def _require_tls(request: Request) -> None:
    if settings.require_tls and request.url.scheme != "https":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "tls_required"})


async def _front_channel_logout(session_id: str) -> None:
    """Placeholder for front-channel logout notifications."""
    return None


async def _back_channel_logout(session_id: str) -> None:
    """Placeholder for back-channel logout notifications."""
    return None
