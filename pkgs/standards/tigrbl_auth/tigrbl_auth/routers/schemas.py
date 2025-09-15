from __future__ import annotations

from typing import Literal, Optional

from tigrbl_auth.deps import BaseModel, EmailStr, Field, constr

from ..typing import StrUUID

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
    refresh_token: Optional[str] = None
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
