"""Salesforce OpenID Connect 1.0 JWT bearer app client wrapper."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Literal, Mapping, Optional, Tuple

from pydantic import ConfigDict, Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OIDC10AppClientBase, RetryingAsyncClient

from .SalesforceOAuth20AppClient import SalesforceOAuth20AppClient, PrivateKeySecret


@ComponentBase.register_type(OIDC10AppClientBase, "SalesforceOIDC10AppClient")
class SalesforceOIDC10AppClient(OIDC10AppClientBase):
    """Discover Salesforce endpoints and request machine tokens over JWT bearer."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    issuer: str
    client_id: str
    user: str
    private_key_pem: Optional[PrivateKeySecret] = Field(default=None, repr=False)
    private_key_jwk: Optional[Mapping[str, Any]] = Field(default=None, repr=False)
    aud: Optional[str] = None
    scope: Optional[str] = None
    jwt_lifetime_seconds: int = Field(default=180, ge=1)
    cache_ttl_seconds: Optional[int] = Field(default=None, ge=1)
    cache_skew_seconds: int = Field(default=30, ge=0)
    discovery_path: str = Field(default="/.well-known/openid-configuration")
    discovery_cache_ttl_seconds: int = Field(default=3600, ge=0)
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )

    type: Literal["SalesforceOIDC10AppClient"] = "SalesforceOIDC10AppClient"

    _discovery_cache: Optional[Tuple[Dict[str, Any], float]] = PrivateAttr(default=None)
    _token_client: Optional[SalesforceOAuth20AppClient] = PrivateAttr(default=None)
    _token_endpoint: Optional[str] = PrivateAttr(default=None)

    async def access_token_payload(self, scope: Optional[str] = None) -> Dict[str, Any]:
        discovery = await self._discover()
        token_endpoint = self._resolve_token_endpoint(discovery)
        client = self._ensure_token_client(token_endpoint)
        effective_scope = scope if scope is not None else self.scope
        return await client.access_token_payload(scope=effective_scope)

    async def access_token(self, scope: Optional[str] = None) -> str:
        payload = await self.access_token_payload(scope=scope)
        token = payload.get("access_token")
        if not isinstance(token, str):
            raise ValueError("access_token missing from Salesforce response")
        return token

    async def _discover(self) -> Dict[str, Any]:
        now = time.time()
        cached = self._discovery_cache
        if cached and self.discovery_cache_ttl_seconds > 0:
            payload, expires_at = cached
            if now < expires_at:
                return dict(payload)

        url = f"{self.issuer.rstrip('/')}{self.discovery_path}"
        async with self.http_client_factory() as client:
            response = await client.get_retry(
                url, headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            data = dict(response.json())

        if self.discovery_cache_ttl_seconds > 0:
            self._discovery_cache = (
                data,
                now + self.discovery_cache_ttl_seconds,
            )

        return data

    def _resolve_token_endpoint(self, discovery: Mapping[str, Any]) -> str:
        endpoint = discovery.get("token_endpoint")
        if isinstance(endpoint, str) and endpoint:
            return endpoint
        return f"{self.issuer.rstrip('/')}/services/oauth2/token"

    def _ensure_token_client(self, token_endpoint: str) -> SalesforceOAuth20AppClient:
        if self._token_client and self._token_endpoint == token_endpoint:
            return self._token_client

        client = SalesforceOAuth20AppClient(
            token_endpoint=token_endpoint,
            client_id=self.client_id,
            user=self.user,
            private_key_pem=self.private_key_pem,
            private_key_jwk=self.private_key_jwk,
            aud=self.aud or self.issuer.rstrip("/"),
            scope=self.scope,
            jwt_lifetime_seconds=self.jwt_lifetime_seconds,
            cache_ttl_seconds=self.cache_ttl_seconds,
            cache_skew_seconds=self.cache_skew_seconds,
            http_client_factory=self.http_client_factory,
        )
        self._token_client = client
        self._token_endpoint = token_endpoint
        return client


__all__ = ["SalesforceOIDC10AppClient"]
