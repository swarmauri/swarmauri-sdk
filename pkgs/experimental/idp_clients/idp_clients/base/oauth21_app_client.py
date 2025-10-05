from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import jwt
from idp_clients.base.utils_http import RetryingAsyncClient

@dataclass(frozen=True)
class OAuth21AppClient:
    token_url: str
    client_id: str
    client_secret: Optional[str] = None
    private_key_jwk: Optional[Dict[str, Any]] = None  # prefer for high-assurance
    cache_skew_sec: int = 30
    _cached: Tuple[str, float] | None = None  # (token, exp)

    async def _client_auth_body(self) -> Dict[str, str]:
        if not self.private_key_jwk:
            return {}
        now = int(time.time())
        assertion = jwt.encode(
            {"iss": self.client_id, "sub": self.client_id, "aud": self.token_url,
             "iat": now, "exp": now + 300, "jti": str(now)},
            key=self.private_key_jwk, algorithm=self.private_key_jwk.get("alg") or "RS256"
        )
        return {
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
        }

    async def _fetch(self, scope: Optional[str]) -> Tuple[str, float]:
        form = {"grant_type": "client_credentials"}
        if scope: form["scope"] = scope
        body, auth = await self._client_auth_body(), None
        if not body and self.client_secret:
            auth = (self.client_id, self.client_secret)
        else:
            form["client_id"] = self.client_id
        async with RetryingAsyncClient() as c:
            r = await c.post_retry(self.token_url, data=form | body, auth=auth,
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
