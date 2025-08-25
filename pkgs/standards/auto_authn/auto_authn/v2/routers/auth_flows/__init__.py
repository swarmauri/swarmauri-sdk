from __future__ import annotations

from ...fastapi_deps import get_async_db
from .common import (
    AUTH_CODES,
    SESSIONS,
    TokenPair,
    _api_backend,
    _jwt,
    _pwd_backend,
    router,
)

# Import flows to register endpoints with the shared router
from . import authorize, login, registration, token, refresh, logout, introspect  # noqa: F401

__all__ = [
    "get_async_db",
    "router",
    "_jwt",
    "_pwd_backend",
    "_api_backend",
    "AUTH_CODES",
    "SESSIONS",
    "TokenPair",
]
