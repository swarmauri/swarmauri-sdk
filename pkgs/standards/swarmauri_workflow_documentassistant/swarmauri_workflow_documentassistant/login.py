"""Bind existing OAuth/OIDC adapters to a one-use browser login session."""

import secrets
import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class OIDCAdmission:
    """Correlate provider state with a host-controlled browser session.

    The web host stores browser_binding in a Secure, HttpOnly, SameSite cookie.
    Identity resolution maps verified provider identity to a local subject.
    """

    login: object
    resolve_identity: Callable
    pending: dict = field(default_factory=dict)
    lifetime: int = 300

    async def begin(self):
        now = time.time()
        self.pending = {
            key: item for key, item in self.pending.items() if item[1] > now
        }
        if len(self.pending) >= 1000:
            raise RuntimeError("Too many pending logins")
        payload = await self.login.auth_url()
        browser_binding = secrets.token_urlsafe(32)
        self.pending[payload["state"]] = (browser_binding, now + self.lifetime)
        return payload, browser_binding

    async def complete(self, code, state, browser_binding):
        expected, expiry = self.pending.get(state, ("", 0))
        if (
            expiry <= time.time()
            or not browser_binding
            or not secrets.compare_digest(expected, browser_binding)
        ):
            raise PermissionError("Login session mismatch or expiry")
        self.pending.pop(state)
        identity = await self.login.exchange_and_identity(code, state)
        return self.resolve_identity(identity)
