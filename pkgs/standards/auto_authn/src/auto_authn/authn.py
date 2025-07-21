"""
auth_authn_idp.authn
~~~~~~~~~~~~~~~~~~~~
Pluggable authentication back‑ends for *pyoidc*.

* **SQLPasswordAuthn** – username / password (bcrypt) against a tenant‑scoped DB
* **APIKeyAuthn**      – opaque, long‑lived API keys (7‑‑90 days)

Both emit a pyoidc‑compatible *authn_event* and can be registered side‑by‑side
under different ACR values.

Design principles
-----------------
• Hard multi‑tenancy – every query filtered by ``tenant.id``.
• All successes / failures are audit‑logged.
• API keys are *never* stored or returned in plaintext; only hashed.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from oic.utils.authn.user import UserAuthnMethod
from oic.utils.time_util import time_sans_frac
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Tenant, User
from .api_keys import verify_api_key

__all__ = ["SQLPasswordAuthn", "APIKeyAuthn"]

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #
_ACR_PASSWORD = "pwd"  # INTERNETPROTOCOLPASSWORD
_ACR_API_KEY = "api_key"  # TOKEN


# --------------------------------------------------------------------------- #
# Helper – build a compliant authn_event                                      #
# --------------------------------------------------------------------------- #
def _build_authn_event(
    sub: str, acr: str, ctx: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Construct the *authn_event* dict required by pyoidc.

    Parameters
    ----------
    sub
        Stable subject identifier.
    acr
        Authentication Context Class Reference (``pwd``, ``api_key``…).
    ctx
        Arbitrary request metadata to embed for downstream auditing.
    """
    return {
        "uid": sub,
        "salt": acr,
        "valid": time_sans_frac(),
        "authn_info": acr,
        "request": ctx or {},
    }


# --------------------------------------------------------------------------- #
# 1. Username / Password back‑end                                             #
# --------------------------------------------------------------------------- #
class SQLPasswordAuthn(UserAuthnMethod):
    """
    Bcrypt‑based username / password verification against the tenant's user set.
    """

    def __init__(
        self,
        db: AsyncSession,
        tenant: Tenant,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(srv=None, authn_info=None, db_store=None)
        self.db = db
        self.tenant = tenant
        self.request_context = request_context or {}

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # Mandatory pyoidc entry point                                          #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    async def verify(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        stmt = (
            select(User)
            .where(User.tenant_id == self.tenant.id)
            .where(User.username == username)
            .limit(1)
        )
        user: User | None = (await self.db.scalars(stmt)).one_or_none()

        if not user:
            log.info(
                "Auth‑fail (user‑not‑found) tenant=%s username=%s",
                self.tenant.slug,
                username,
            )
            return None

        if not user.is_active or not user.verify_password(password):
            log.info(
                "Auth‑fail (bad‑credentials) tenant=%s username=%s",
                self.tenant.slug,
                username,
            )
            return None

        log.debug(
            "Auth‑success (password) tenant=%s sub=%s",
            self.tenant.slug,
            user.sub,
        )
        return _build_authn_event(user.sub, _ACR_PASSWORD, self.request_context)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # UI hook (unused in API‑first flows)                                   #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
        raise NotImplementedError(
            "Interactive login flow not implemented – "
            "submit credentials to /password-login instead."
        )


# --------------------------------------------------------------------------- #
# 2. API‑Key back‑end                                                        #
# --------------------------------------------------------------------------- #
class APIKeyAuthn(UserAuthnMethod):
    """
    Verifies long‑lived opaque API keys created via ``POST /api-keys``.

    Parameters
    ----------
    raw_key
        The API key presented by the caller (full secret, as received).
    db
        Tenant‑scoped async SQLAlchemy session.
    tenant
        Tenant object for multi‑tenant isolation.
    request_context
        Additional metadata to embed in the *authn_event*.
    """

    def __init__(
        self,
        raw_key: str,
        db: AsyncSession,
        tenant: Tenant,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(srv=None, authn_info=None, db_store=None)
        self._raw_key = raw_key
        self.db = db
        self.tenant = tenant
        self.request_context = request_context or {}

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # Mandatory pyoidc entry point                                          #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    async def verify(  # noqa: D401
        self, *args: Any, **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        rec = await verify_api_key(self._raw_key, self.db, self.tenant.id)
        if not rec:
            log.info(
                "Auth‑fail (api‑key‑invalid) tenant=%s prefix=%s",
                self.tenant.slug,
                self._raw_key[:8],
            )
            return None

        log.debug(
            "Auth‑success (api‑key) tenant=%s key_id=%s sub=%s",
            self.tenant.slug,
            rec.id,
            rec.owner_id,
        )
        return _build_authn_event(rec.owner_id, _ACR_API_KEY, self.request_context)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # UI hook (unused – API keys are non‑interactive)                       #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
        raise NotImplementedError("API‑key authn backend is non‑interactive.")
