"""Salesforce OAuth 2.1 JWT bearer app client wrapper."""

from __future__ import annotations

from typing import Any, Callable, Dict, Literal, Mapping, Optional

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21AppClientBase, RetryingAsyncClient

from .SalesforceOAuth20AppClient import SalesforceOAuth20AppClient


@ComponentBase.register_type(OAuth21AppClientBase, "SalesforceOAuth21AppClient")
class SalesforceOAuth21AppClient(OAuth21AppClientBase):
    """Reuse the OAuth 2.0 JWT bearer client with OAuth 2.1 semantics."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    token_endpoint: str
    client_id: str
    user: str
    private_key_jwk: Mapping[str, Any]
    aud: Optional[str] = None
    scope: Optional[str] = None
    jwt_lifetime_seconds: int = Field(default=180, ge=1)
    cache_ttl_seconds: Optional[int] = Field(default=None, ge=1)
    cache_skew_seconds: int = Field(default=30, ge=0)
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )

    type: Literal["SalesforceOAuth21AppClient"] = "SalesforceOAuth21AppClient"

    async def access_token_payload(self, scope: Optional[str] = None) -> Dict[str, Any]:
        client = SalesforceOAuth20AppClient(
            token_endpoint=self.token_endpoint,
            client_id=self.client_id,
            user=self.user,
            private_key_jwk=self.private_key_jwk,
            aud=self.aud,
            scope=self.scope,
            jwt_lifetime_seconds=self.jwt_lifetime_seconds,
            cache_ttl_seconds=self.cache_ttl_seconds,
            cache_skew_seconds=self.cache_skew_seconds,
            http_client_factory=self.http_client_factory,
        )
        return await client.access_token_payload(scope=scope)

    async def access_token(self, scope: Optional[str] = None) -> str:
        payload = await self.access_token_payload(scope=scope)
        token = payload.get("access_token")
        if not isinstance(token, str):
            raise ValueError("access_token missing from Salesforce response")
        return token


__all__ = ["SalesforceOAuth21AppClient"]
