"""GitLab OIDC 1.0 client credentials app client implementation."""

from __future__ import annotations

import time
from typing import Any, Callable, Mapping, Optional, Tuple

from pydantic import ConfigDict, Field, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OIDC10AppClientBase
from swarmauri_base.auth_idp.http import RetryingAsyncClient


@ComponentBase.register_type(OIDC10AppClientBase, "GitLabOIDC10AppClient")
class GitLabOIDC10AppClient(OIDC10AppClientBase):
    """Request client credentials tokens using GitLab's OIDC discovery metadata."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    issuer: str
    client_id: str
    client_secret: SecretStr
    cache_skew_seconds: int = Field(default=30, ge=0)
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )
    cached_token: Optional[Tuple[str, float]] = Field(
        default=None, exclude=True, repr=False
    )
    discovery_cache: Optional[Mapping[str, Any]] = Field(
        default=None, exclude=True, repr=False
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    async def _metadata(self) -> Mapping[str, Any]:
        if self.discovery_cache is None:
            url = f"{self.issuer.rstrip('/')}/.well-known/openid-configuration"
            async with self.http_client_factory() as client:
                response = await client.get_retry(
                    url, headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                self.discovery_cache = response.json()
        return self.discovery_cache

    async def _fetch_token(self, scope: Optional[str]) -> Tuple[str, float]:
        metadata = await self._metadata()
        form = {"grant_type": "client_credentials"}
        if scope:
            form["scope"] = scope
        auth = (self.client_id, self._client_secret_value())
        async with self.http_client_factory() as client:
            response = await client.post_retry(
                metadata["token_endpoint"],
                data=form,
                auth=auth,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
        expires_at = time.time() + int(payload.get("expires_in", 3600))
        return payload["access_token"], expires_at

    async def access_token(self, scope: Optional[str] = None) -> str:
        cached = self.cached_token
        now = time.time()
        if cached and now < cached[1] - self.cache_skew_seconds:
            return cached[0]
        token, expires_at = await self._fetch_token(scope)
        self.cached_token = (token, expires_at)
        return token
