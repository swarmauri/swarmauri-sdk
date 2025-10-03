from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import time
from idp_clients.base.utils_http import RetryingAsyncClient

@dataclass(frozen=True)
class FacebookOAuth20AppClient:
    """OAuth 2.0 App token via client_credentials (Graph API).

    - graph_base: e.g., https://graph.facebook.com
    - version: e.g., v19.0
    """
    graph_base: str = "https://graph.facebook.com"
    version: str = "v19.0"
    client_id: str = ""
    client_secret: str = ""
    cache_skew_sec: int = 30
    _cached: Tuple[str, float] | None = None

    def _token_ep(self) -> str:
        return f"{self.graph_base.rstrip('/')}/{self.version}/oauth/access_token"

    async def access_token(self) -> str:
        # Facebook app access token is obtained with grant_type=client_credentials
        if self._cached and time.time() < self._cached[1] - self.cache_skew_sec:
            return self._cached[0]
        form = {"grant_type":"client_credentials", "client_id": self.client_id, "client_secret": self.client_secret}
        async with RetryingAsyncClient() as c:
            r = await c.post_retry(self._token_ep(), data=form, headers={"Accept":"application/json"})
            r.raise_for_status()
            tok = r.json()
        t = tok.get("access_token")
        exp = time.time() + int(tok.get("expires_in", 3600))
        object.__setattr__(self, "_cached", (t, exp))
        return t
