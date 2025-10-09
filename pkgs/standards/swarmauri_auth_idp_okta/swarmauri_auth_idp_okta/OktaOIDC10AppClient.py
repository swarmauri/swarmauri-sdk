"""Okta OIDC 1.0 client credentials app client implementation."""

from __future__ import annotations

import time
from typing import Any, Callable, Mapping, Optional, Tuple

from pydantic import ConfigDict, Field, PrivateAttr, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OIDC10AppClientBase, RetryingAsyncClient


@ComponentBase.register_type(OIDC10AppClientBase, "OktaOIDC10AppClient")
class OktaOIDC10AppClient(OIDC10AppClientBase):
    """Request machine-to-machine tokens using Okta's OIDC discovery metadata."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    issuer: str
    client_id: str
    client_secret: SecretStr
    cache_skew_seconds: int = Field(default=30, ge=0)
    discovery_cache_ttl_seconds: int = Field(default=3600, ge=0)
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )

    _cached_token: Optional[Tuple[str, float]] = PrivateAttr(default=None)
    _discovery_cache: Optional[Tuple[Mapping[str, Any], float]] = PrivateAttr(
        default=None
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    async def _discovery(self) -> Mapping[str, Any]:
        now = time.time()
        cached = self._discovery_cache
        if cached and now < cached[1]:
            return cached[0]
        url = f"{self.issuer.rstrip('/')}/.well-known/openid-configuration"
        async with self.http_client_factory() as client:
            response = await client.get_retry(
                url,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            payload: Mapping[str, Any] = response.json()
        if self.discovery_cache_ttl_seconds > 0:
            self._discovery_cache = (payload, now + self.discovery_cache_ttl_seconds)
        return payload

    async def _fetch_token(self, scope: Optional[str]) -> Tuple[str, float]:
        metadata = await self._discovery()
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
        token = payload.get("access_token")
        if not token:
            raise ValueError("access_token missing from Okta response")
        expires_at = time.time() + int(payload.get("expires_in", 3600))
        return token, expires_at

    async def access_token(self, scope: Optional[str] = None) -> str:
        cached = self._cached_token
        now = time.time()
        if cached and now < cached[1] - self.cache_skew_seconds:
            return cached[0]
        token, expires_at = await self._fetch_token(scope)
        self._cached_token = (token, expires_at)
        return token


__all__ = ["OktaOIDC10AppClient"]
