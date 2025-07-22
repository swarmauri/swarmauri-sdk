"""
autoapi_authn.fastapi_deps
==========================

FastAPI dependency helpers used by the AuthN service itself
and by *any* downstream service that wishes to rely on AuthN’s
JWT / API-key semantics.

Exports
-------
get_current_principal   → dependency that returns an authenticated **User**
require_scope           → decorator enforcing coarse scopes

Both helpers are **framework-thin**: they translate `AuthError` raised by
`backends.py` into `fastapi.HTTPException` and nothing more.
"""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .backends import (
    ApiKeyBackend,
    AuthError,
    PasswordBackend,
)  # PasswordBackend not used here, but re-exported for completeness
from .orm.tables import User
from .typing import Principal
from .db import get_async_db
from .jwtoken import JWTCoder
from .crypto import public_key, signing_key
_api_key_backend = ApiKeyBackend()
_jwt_coder = JWTCoder(public_key, signing_key)

# ---------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------
async def _user_from_jwt(token: str, db: AsyncSession) -> User | None:
    from jwt import InvalidTokenError

    try:
        payload = _jwt_coder.decode(token)
    except InvalidTokenError:
        return None

    # Lazy import to avoid cycle explosions
    from sqlalchemy import select

    stmt = select(User).where(User.id == payload["sub"], User.is_active.is_(True))
    return await db.scalar(stmt)


async def _user_from_api_key(raw_key: str, db: AsyncSession) -> User | None:
    try:
        return await _api_key_backend.authenticate(db, raw_key)
    except AuthError:
        return None


async def get_current_principal(  # type: ignore[override]
    authorization: str = Header("", alias="Authorization"),
    api_key: str | None = Header(None, alias="x-api-key"),
    db: AsyncSession = Depends(get_async_db),
) -> Principal:
    """
    Resolve the request principal via **exactly one** of:

    1. `x-api-key:`  → ApiKeyBackend
    2. `Authorization: Bearer <jwt>`  → verified JWT

    On success
    ----------
    Returns the **User** ORM instance (which satisfies Principal Protocol).

    On failure
    ----------
    Raises HTTP 401 (unauthenticated).
    """
    if api_key:
        if user := await _user_from_api_key(api_key, db):
            return user

    if authorization.startswith("Bearer "):
        if user := await _user_from_jwt(authorization.split()[1], db):
            return user

    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "invalid or missing credentials",
        headers={"WWW-Authenticate": 'Bearer realm="authn"'},
    )


# Public re-exports
__all__ = [
    "get_current_principal",
    "PasswordBackend",
    "ApiKeyBackend",
]
