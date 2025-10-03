from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from idp_clients.base.utils_http import RetryingAsyncClient

@dataclass(frozen=True)
class OIDC10AppClient:
    issuer: str
    client_id: str
    client_secret: str
    cache_skew_sec: int = 30
    _disc: Dict[str, Any] | None = None
    _cached: Tuple[str, float] | None = None

    async def _discover(self) -> Dict[str, Any]:
        if self._disc: return self._disc
        url = f"{self.issuer.rstrip('/')}/.well-known/openid-configuration"
        async with RetryingAsyncClient() as c:
            r = await c.get_retry(url, headers={"Accept": "application/json"})
            r.raise_for_status()
            d = r.json()
        object.__setattr__(self, "_disc", d)
        return d

    async def access_token(self, scope: Optional[str] = None) -> str:
        if self._cached and time.time() < self._cached[1] - self.cache_skew_sec:
            return self._cached[0]
        disc = await self._discover()
        form = {"grant_type": "client_credentials"}
        if scope: form["scope"] = scope
        async with RetryingAsyncClient() as c:
            r = await c.post_retry(disc["token_endpoint"], data=form,
                                   auth=(self.client_id, self.client_secret),
                                   headers={"Accept": "application/json"})
            r.raise_for_status()
            tok = r.json()
        t, exp = tok["access_token"], time.time() + int(tok.get("expires_in", 3600))
        object.__setattr__(self, "_cached", (t, exp))
        return t
