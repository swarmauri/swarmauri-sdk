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

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import (
    APIKeyHeader,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
import contextvars
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


# ---------------------------------------------------------------------
# Backends + Coder
# ---------------------------------------------------------------------
_api_key_backend = ApiKeyBackend()
_jwt_coder = JWTCoder(public_key, signing_key)

# ---------------------------------------------------------------------
# Public ContextVar – used by AutoAPI row filters
# ---------------------------------------------------------------------
principal_var: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "principal", default=None
)


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


async def _user_from_api_key(raw_key: str, db: AsyncSession) -> Principal | None:
    try:
        principal, _ = await _api_key_backend.authenticate(db, raw_key)
        return principal
    except AuthError:
        return None


# ---------------------------------------------------------------------
# NEW — AuthNProvider‑compatible helper
# ---------------------------------------------------------------------
_bearer_scheme = HTTPBearer(auto_error=False)
_api_key_scheme = APIKeyHeader(name="x-api-key", auto_error=False)


async def get_principal(  # <-- AutoAPI calls this
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
    api_key: str | None = Security(_api_key_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> dict:
    """
    Return a lightweight principal dict that AutoAPI understands:
        { "sub": "<user_id>", "tid": "<tenant_id>" }
    Raises HTTP 401 on failure.
    """
    user = await get_current_principal(  # reuse the existing logic
        credentials=credentials, api_key=api_key, db=db
    )
    principal = {"sub": str(user.id), "tid": str(user.tenant_id)}

    # cache in both request.state and ContextVar
    request.state.principal = principal
    principal_var.set(principal)
    return principal


async def get_current_principal(  # type: ignore[override]
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
    api_key: str | None = Security(_api_key_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> Principal:
    """
    Resolve the request principal via **exactly one** of:

    1. `x-api-key:`  → ApiKeyBackend
    2. `Authorization: Bearer <jwt>`  → verified JWT

    On success
    ----------
    Returns the principal ORM instance (which satisfies ``Principal`` Protocol).

    On failure
    ----------
    Raises HTTP 401 (unauthenticated).
    """
    if api_key:
        if user := await _user_from_api_key(api_key, db):
            return user

    if credentials:
        if user := await _user_from_jwt(credentials.credentials, db):
            return user

    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "invalid or missing credentials",
        headers={"WWW-Authenticate": 'Bearer realm="authn"'},
    )


# Public re-exports
__all__ = [
    "get_current_principal",
    "get_principal",  # <- NEW
    "principal_var",  # <- used by row_filters
    "PasswordBackend",
    "ApiKeyBackend",
]
