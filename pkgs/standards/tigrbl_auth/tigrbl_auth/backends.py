"""
tigrbl_authn.backends
======================

Framework-agnostic credential verification helpers.

Exports
-------
AuthError         : Exception raised on any authentication failure.
PasswordBackend   : Validates username/email + password.
ApiKeyBackend     : Validates raw API key string.

Both back-ends return the **User** ORM row on success, allowing callers
to access tenant_id, scopes, etc., without an extra query.

Note
----
No FastAPI or HTTP details here; mapping AuthError → HTTPException
is handled in `fastapi_deps.py` or route handlers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Optional

from typing import TYPE_CHECKING

from sqlalchemy import Select, or_, select
from tigrbl.engine import HybridSession as AsyncSession

from .crypto import verify_pw
from .typing import Principal

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from .orm import ApiKey, Client, ServiceKey, User


def _ApiKey():  # pragma: no cover - thin import wrapper
    from .orm import ApiKey

    return ApiKey


def _ServiceKey():  # pragma: no cover - thin import wrapper
    from .orm import ServiceKey

    return ServiceKey


def _Client():  # pragma: no cover - thin import wrapper
    from .orm import Client

    return Client


def _User():  # pragma: no cover - thin import wrapper
    from .orm import User

    return User


class AuthError(Exception):
    """Raised when authentication fails for any reason."""

    def __init__(self, reason: str = "authentication failed"):
        super().__init__(reason)
        self.reason = reason


# ---------------------------------------------------------------------
# Password-based authentication
# ---------------------------------------------------------------------
class PasswordBackend:
    """
    Authenticate a user by username *or* email plus plaintext password.

    Usage
    -----
    >>> backend = PasswordBackend()
    >>> user = await backend.authenticate(db, "alice", "pa$$w0rd")
    """

    async def _get_user_stmt(self, identifier: str) -> Select[tuple["User"]]:
        user = _User()
        return select(user).where(
            or_(user.username == identifier, user.email == identifier),
            user.is_active.is_(True),
        )

    async def authenticate(
        self, db: AsyncSession, identifier: str, password: str
    ) -> User:
        row: Optional["User"] = await db.scalar(await self._get_user_stmt(identifier))
        if not row or not verify_pw(password, row.password_hash):
            raise AuthError("invalid username/email or password")
        return row


# ---------------------------------------------------------------------
# API-key authentication
# ---------------------------------------------------------------------
class ApiKeyBackend:
    """
    Authenticate a principal via raw API key string.

    * Only active, non-expired keys are valid.
    * The raw secret is never stored; verification is via BLAKE2b-256 digest.
    """

    async def _get_key_stmt(self, digest: str) -> Select[tuple["ApiKey"]]:
        now = datetime.now(timezone.utc)
        api_key = _ApiKey()
        return select(api_key).where(
            api_key.digest == digest,
            or_(api_key.valid_to.is_(None), api_key.valid_to > now),
        )

    async def _get_service_key_stmt(self, digest: str) -> Select[tuple["ServiceKey"]]:
        now = datetime.now(timezone.utc)
        svc_key = _ServiceKey()
        return select(svc_key).where(
            svc_key.digest == digest,
            or_(svc_key.valid_to.is_(None), svc_key.valid_to > now),
        )

    async def _get_client_stmt(self) -> Select[tuple["Client"]]:
        client = _Client()
        return select(client).where(client.is_active.is_(True))

    async def authenticate(
        self, db: AsyncSession, api_key: str
    ) -> tuple[Principal, str]:
        api_key_cls = _ApiKey()
        digest = api_key_cls.digest_of(api_key)

        key_row: Optional["ApiKey"] = await db.scalar(await self._get_key_stmt(digest))
        if key_row and key_row.user:
            if not key_row.user.is_active:
                raise AuthError("user is inactive")
            key_row.touch()
            return key_row.user, "user"

        svc_row: Optional["ServiceKey"] = await db.scalar(
            await self._get_service_key_stmt(digest)
        )
        if svc_row:
            if not svc_row.service.is_active:
                raise AuthError("service is inactive")
            svc_row.touch()
            return svc_row.service, "service"

        clients: Iterable["Client"] = await db.scalars(await self._get_client_stmt())
        for client in clients:
            if client.verify_secret(api_key):
                return client, "client"

        raise AuthError("API key invalid, revoked, or expired")
