"""Shared utilities and schemas for auth flow routers."""

from __future__ import annotations

from typing import Literal, Optional

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field, constr

from ...jwtoken import JWTCoder
from ...backends import ApiKeyBackend, PasswordBackend
from ...runtime_cfg import settings
from ...typing import StrUUID

# Backends and token coder used across flows
_jwt = JWTCoder.default()
_pwd_backend = PasswordBackend()
_api_backend = ApiKeyBackend()

# Grant type configuration
_ALLOWED_GRANT_TYPES = {"password", "authorization_code"}
if settings.enable_rfc8628:
    _ALLOWED_GRANT_TYPES.add("urn:ietf:params:oauth:grant-type:device_code")

# In-memory stores for auth codes and sessions
AUTH_CODES: dict[str, dict] = {}
SESSIONS: dict[str, dict] = {}


def _require_tls(request: Request) -> None:
    """Enforce TLS when ``require_tls`` is enabled."""
    if settings.require_tls and request.url.scheme != "https":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"error": "tls_required"})


async def _front_channel_logout(session_id: str) -> None:
    """Placeholder for front-channel logout notifications."""
    return None


async def _back_channel_logout(session_id: str) -> None:
    """Placeholder for back-channel logout notifications."""
    return None


# ---------------------------------------------------------------------------
# Pydantic schemas shared across flows
# ---------------------------------------------------------------------------
_username = constr(strip_whitespace=True, min_length=3, max_length=80)
_password = constr(min_length=8, max_length=256)


class RegisterIn(BaseModel):
    tenant_slug: constr(strip_whitespace=True, min_length=3, max_length=120)
    username: _username
    email: EmailStr
    password: _password


class CredsIn(BaseModel):
    identifier: constr(strip_whitespace=True, min_length=3, max_length=120)
    password: _password


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")
    id_token: Optional[str] = None


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    id_token_hint: str


class IntrospectOut(BaseModel):
    active: bool
    sub: Optional[StrUUID] = None
    tid: Optional[StrUUID] = None
    kind: Optional[str] = None


class PasswordGrantForm(BaseModel):
    grant_type: Literal["password"]
    username: str
    password: str


class AuthorizationCodeGrantForm(BaseModel):
    grant_type: Literal["authorization_code"]
    code: str
    redirect_uri: str
    client_id: str
    code_verifier: Optional[str] = None
