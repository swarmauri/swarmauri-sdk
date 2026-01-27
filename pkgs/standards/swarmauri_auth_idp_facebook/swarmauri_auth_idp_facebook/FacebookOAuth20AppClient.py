"""Facebook OAuth 2.0 client-credentials token helper."""

from __future__ import annotations

import time
from typing import Callable, Literal, Mapping, Optional, Tuple

from pydantic import ConfigDict, Field, PrivateAttr, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20AppClientBase, RetryingAsyncClient


@ComponentBase.register_type(OAuth20AppClientBase, "FacebookOAuth20AppClient")
class FacebookOAuth20AppClient(OAuth20AppClientBase):
    """Obtain Facebook app access tokens using the client credentials grant."""

    model_config = ConfigDict(extra="forbid")

    graph_base: str = Field(default="https://graph.facebook.com")
    version: str = Field(default="v19.0")
    client_id: str
    client_secret: SecretStr
    cache_skew_sec: int = Field(default=30)

    type: Literal["FacebookOAuth20AppClient"] = "FacebookOAuth20AppClient"

    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )
    _token_cache: Optional[Tuple[str, float]] = PrivateAttr(default=None)

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _token_endpoint(self) -> str:
        return f"{self.graph_base.rstrip('/')}/{self.version}/oauth/access_token"

    async def _request_token(self, form: Mapping[str, str]) -> Mapping[str, str]:
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                self._token_endpoint(),
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def access_token(self, scope: Optional[str] = None) -> str:
        del scope  # Facebook app tokens do not support dynamic scopes.
        cached = self._token_cache
        now = time.time()
        if cached and now < cached[1] - self.cache_skew_sec:
            return cached[0]
        form = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self._client_secret_value(),
        }
        token_response = await self._request_token(form)
        token = token_response.get("access_token")
        if not token:
            raise ValueError("access_token missing from Facebook response")
        expires_in = int(token_response.get("expires_in", 3600))
        expiry = now + max(1, expires_in)
        self._token_cache = (token, expiry)
        return token


__all__ = ["FacebookOAuth20AppClient"]
