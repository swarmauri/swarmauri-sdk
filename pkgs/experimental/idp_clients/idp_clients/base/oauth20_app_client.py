from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional, Tuple
from idp_clients.base.utils_http import RetryingAsyncClient

@dataclass(frozen=True)
class OAuth20AppClient:
    token_url: str
    client_id: str
    client_secret: str
    cache_skew_sec: int = 30
    _cached: Tuple[str, float] | None = None

    async def _fetch(self, scope: Optional[str]) -> Tuple[str, float]:
        form = {"grant_type": "client_credentials"}
        if scope: form["scope"] = scope
        async with RetryingAsyncClient() as c:
            r = await c.post_retry(self.token_url, data=form, auth=(self.client_id, self.client_secret),
                                   headers={"Accept": "application/json"})
            r.raise_for_status()
            tok = r.json()
        return tok["access_token"], time.time() + int(tok.get("expires_in", 3600))

    async def access_token(self, scope: Optional[str] = None) -> str:
        if self._cached and time.time() < self._cached[1] - self.cache_skew_sec:
            return self._cached[0]
        t, exp = await self._fetch(scope)
        object.__setattr__(self, "_cached", (t, exp))
        return t
