"""ORM table models for tigrbl_auth."""

from __future__ import annotations

from tigrbl.orm.tables import Base

from ..runtime_cfg import settings
from .api_key import ApiKey
from .auth_code import AuthCode
from .auth_session import AuthSession
from .client import Client, _CLIENT_ID_RE
from .device_code import DeviceCode
from .pushed_authorization_request import PushedAuthorizationRequest
from .revoked_token import RevokedToken
from .service import Service
from .service_key import ServiceKey
from .tenant import Tenant
from .user import User

__all__ = [
    "Base",
    "Tenant",
    "Client",
    "User",
    "Service",
    "ApiKey",
    "ServiceKey",
    "AuthSession",
    "AuthCode",
    "DeviceCode",
    "RevokedToken",
    "PushedAuthorizationRequest",
    "_CLIENT_ID_RE",
    "settings",
]
