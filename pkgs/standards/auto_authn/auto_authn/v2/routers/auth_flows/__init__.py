"""Modular authentication and authorization flows."""

from fastapi import APIRouter

from ...fastapi_deps import get_async_db
from .common import AUTH_CODES, SESSIONS, _api_backend, _jwt, _pwd_backend
from . import authorization, introspect, login, logout, refresh, registration, token

router = APIRouter()
router.include_router(registration.router)
router.include_router(login.router)
router.include_router(authorization.router)
router.include_router(token.router)
router.include_router(logout.router)
router.include_router(refresh.router)
router.include_router(introspect.router)

__all__ = [
    "router",
    "_jwt",
    "_pwd_backend",
    "_api_backend",
    "AUTH_CODES",
    "SESSIONS",
    "get_async_db",
]
