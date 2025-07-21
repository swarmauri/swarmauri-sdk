"""
auth_authn_idp.authn
~~~~~~~~~~~~~~~~~~~~
Pluggable authentication back‑end for pyoidc that verifies a username /
password against the database (bcrypt hashes) and returns the
`authn_event` structure expected by the OIDC core.

* Compatible with multi‑tenant deployments.
* Emits audit‑log messages for every success / failure.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from oic.utils.authn.user import UserAuthnMethod
from oic.utils.time_util import time_sans_frac
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Tenant, User

log = logging.getLogger("auth_authn.authn")


class SQLPasswordAuthn(UserAuthnMethod):
    """
    SQLAlchemy‑backed username / password verifier.


    Parameters
    ----------
    db : AsyncSession
        A *bound* async session (scoped to the current request/tenant).
    tenant : Tenant
        The tenant object whose user table we should query.
    request_context : Dict[str, Any], optional
        Arbitrary context you want to keep with the authn_event; e.g. IP.
    """

    def __init__(
        self,
        db: AsyncSession,
        tenant: Tenant,
        request_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            srv=None,  # will be injected by pyoidc
            authn_info=None,  # we fill in ACR dynamically
            db_store=None,
        )
        self.db = db
        self.tenant = tenant
        self.request_context = request_context or {}

    # ------------------------------------------------------------------ #
    # Mandatory interface – pyoidc calls these                           #
    # ------------------------------------------------------------------ #
    async def verify(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Given a username+password, return an **authn_event** dict on success or
        `None` on failure.  Async because we hit the DB.
        """
        stmt = (
            select(User)
            .where(User.tenant_id == self.tenant.id)
            .where(User.username == username)
            .limit(1)
        )
        user: User | None = (await self.db.scalars(stmt)).one_or_none()

        if not user:
            log.info(
                "Auth‑fail (no such user) tenant=%s username=%s",
                self.tenant.slug,
                username,
            )
            return None

        if not user.is_active or not user.verify_password(password):
            log.info(
                "Auth‑fail (bad credentials) tenant=%s username=%s",  #
                self.tenant.slug,
                username,
            )
            return None

        # Success – build authn_event as per pyoidc spec
        authn_event = {
            "uid": user.sub,  # SUBJECT identifier
            "salt": "pwd",  # track the method used (pwd vs mfa)
            "valid": time_sans_frac(),  # epoch seconds
            "authn_info": "pwd",  # maps to ACR value INTERNETPROTOCOLPASSWORD
            "request": self.request_context,
        }

        log.debug(
            "Auth‑success tenant=%s user=%s sub=%s",
            self.tenant.slug,
            username,
            user.sub,
        )
        return authn_event

    # ------------------------------------------------------------------ #
    # Optional – UI / redirect hooks                                     #
    # ------------------------------------------------------------------ #
    def __call__(self, *args, **kwargs):  # noqa: D401  (pyoidc API)
        """
        In a pure API‑first IdP we don't run an HTML login flow inside the
        Authorize endpoint; instead, credentials are POSTed directly to
        `/password-login`.  Therefore this method is **unused** and raises.
        """
        raise NotImplementedError(
            "Interactive login flow not implemented – "
            "use JSON API /password-login to obtain cookies, "
            "or integrate MFA module."
        )
