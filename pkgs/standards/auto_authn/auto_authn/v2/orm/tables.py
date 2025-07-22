"""
autoapi_authn.orm.tables
~~~~~~~~~~~~~~~~~~~~~~~~

Canonical SQLAlchemy models for the authentication service.

* Tenant  – logical partition; owner of users, clients, keys.
* Client  – OIDC / OAuth2 relying party registration.
* User    – human principal with bcrypt-hashed password.
* ApiKey  – machine credential (digest stored, raw secret shown once).

All models inherit GUIDPk, Timestamped, and (where relevant) TenantBound
from *autoapi.v2.mixins* so they automatically gain:
    • UUID primary keys
    • created_at / updated_at audit stamps
    • row-level security filters via TenantBound
"""

from __future__ import annotations

import re
import uuid
from typing import Annotated, Final

from autoapi.v2.types import (
    String,
)
from sqlalchemy.orm import mapped_column
from autoapi.v2.tables import (
    Tenant,
    Client as ClientBase,
    User as UserBase,
    ApiKey,
)
from ..crypto import hash_pw  # bcrypt helper shared across package

# ────────────────────────────────────────────────────────────────────
# Utility type alias for 36-char UUID strings
_UUID = Annotated[str, mapped_column(String(36), default=lambda: str(uuid.uuid4()))]

# Regular-expression for a valid client_id (RFC 6749 allows many forms)
_CLIENT_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9\-_]{8,64}$")


# --------------------------------------------------------------------
class Client(ClientBase):  # Tenant FK via mix-in
    # ----------------------------------------------------------------
    @classmethod
    def new(
        cls,
        tenant_id: uuid.UUID,
        client_id: str,
        client_secret: str,
        redirects: list[str],
    ):
        if not _CLIENT_ID_RE.fullmatch(client_id):
            raise ValueError("invalid client_id format")
        secret_hash = hash_pw(client_secret)
        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret_hash=secret_hash,
            redirect_uris=" ".join(redirects),
        )

    def verify_secret(self, plain: str) -> bool:
        from ..crypto import verify_pw  # local import to avoid cycle

        return verify_pw(plain, self.client_secret_hash)


# --------------------------------------------------------------------
class User(UserBase):
    """Human principal with authentication credentials."""

    # ----------------------------------------------------------------
    @classmethod
    def new(cls, tenant_id: uuid.UUID, username: str, email: str, password: str):
        return cls(
            tenant_id=tenant_id,
            username=username,
            email=email,
        )

    def verify_password(self, plain: str) -> bool:
        from ..crypto import verify_pw

        return verify_pw(plain, self.password_hash)


__all__ = ["ApiKey", "User", "Tenant", "Client"]
