"""
autoapi_authn.backends
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
from typing import Iterable, Optional, TYPE_CHECKING

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .crypto import verify_pw
from .typing import Principal

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from .orm.tables import ApiKey, Client, ServiceKey, User


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
        from .orm.tables import User

        return select(User).where(
            or_(User.username == identifier, User.email == identifier),
            User.is_active.is_(True),
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
        from .orm.tables import ApiKey

        now = datetime.now(timezone.utc)
        return select(ApiKey).where(
            ApiKey.digest == digest,
            or_(ApiKey.valid_to.is_(None), ApiKey.valid_to > now),
        )

    async def _get_service_key_stmt(self, digest: str) -> Select[tuple["ServiceKey"]]:
        from .orm.tables import ServiceKey

        now = datetime.now(timezone.utc)
        return select(ServiceKey).where(
            ServiceKey.digest == digest,
            or_(ServiceKey.valid_to.is_(None), ServiceKey.valid_to > now),
        )

    async def _get_client_stmt(self) -> Select[tuple["Client"]]:
        from .orm.tables import Client

        return select(Client).where(Client.is_active.is_(True))

    async def authenticate(
        self, db: AsyncSession, api_key: str
    ) -> tuple[Principal, str]:
        digest = ApiKey.digest_of(api_key)

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
