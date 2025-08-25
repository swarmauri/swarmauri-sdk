"""Aggregate OAuth and OIDC flow routers."""

from fastapi import APIRouter

from ..fastapi_deps import get_async_db as _get_async_db
from .flows import (
    authorization,
    credentials,
    introspection,
    logout,
    refresh,
    token,
    common,
)

router = APIRouter()
router.include_router(credentials.router)
router.include_router(authorization.router)
router.include_router(token.router)
router.include_router(logout.router)
router.include_router(refresh.router)
router.include_router(introspection.router)

# Re-export shared state for tests and external modules
AUTH_CODES = common.AUTH_CODES
SESSIONS = common.SESSIONS
_jwt = common._jwt
_pwd_backend = common._pwd_backend
get_async_db = _get_async_db
