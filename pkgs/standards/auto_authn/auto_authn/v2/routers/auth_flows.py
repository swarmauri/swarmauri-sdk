from __future__ import annotations

from fastapi import APIRouter

from .authn import router as authn_router
from .authz import router as authz_router
from .shared import _jwt, _pwd_backend, AUTH_CODES, SESSIONS

router = APIRouter()
router.include_router(authn_router)
router.include_router(authz_router)

__all__ = ["router", "_jwt", "_pwd_backend", "AUTH_CODES", "SESSIONS"]
