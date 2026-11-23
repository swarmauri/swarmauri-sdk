"""Gitea OAuth 2.0 client credentials app client implementation."""

from __future__ import annotations

import time
from typing import Callable, Optional, Tuple

from pydantic import ConfigDict, Field, PrivateAttr, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20AppClientBase
from swarmauri_base.auth_idp.http import RetryingAsyncClient


@ComponentBase.register_type(OAuth20AppClientBase, "GiteaOAuth20AppClient")
class GiteaOAuth20AppClient(OAuth20AppClientBase):
    """Request machine-to-machine tokens from the Gitea OAuth 2.0 endpoint."""

    model_config = ConfigDict(extra="forbid")

    base_url: str
    client_id: str
    client_secret: SecretStr
    cache_skew_seconds: int = Field(default=30, ge=0)

    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )
    _cached_token: Optional[Tuple[str, float]] = PrivateAttr(default=None)

    def _token_endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}/login/oauth/access_token"

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    async def _fetch_token(self, scope: Optional[str]) -> Tuple[str, float]:
        form = {"grant_type": "client_credentials"}
        if scope:
            form["scope"] = scope
        auth = (self.client_id, self._client_secret_value())
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                self._token_endpoint(),
                data=form,
                auth=auth,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
        expires_at = time.time() + int(payload.get("expires_in", 3600))
        return payload["access_token"], expires_at

    async def access_token(self, scope: Optional[str] = None) -> str:
        cached = self._cached_token
        now = time.time()
        if cached and now < cached[1] - self.cache_skew_seconds:
            return cached[0]
        token, expires_at = await self._fetch_token(scope)
        self._cached_token = (token, expires_at)
        return token
