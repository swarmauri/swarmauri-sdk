"""Salesforce OAuth 2.0 JWT bearer app client implementation."""

from __future__ import annotations

import time
from typing import Any, Callable, ClassVar, Dict, Literal, Mapping, Optional, Tuple

import jwt
from pydantic import ConfigDict, Field, PrivateAttr, SecretBytes, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20AppClientBase, RetryingAsyncClient


PrivateKeySecret = SecretStr | SecretBytes


@ComponentBase.register_type(OAuth20AppClientBase, "SalesforceOAuth20AppClient")
class SalesforceOAuth20AppClient(OAuth20AppClientBase):
    """Request machine-to-machine access tokens using Salesforce's JWT bearer flow."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    JWT_GRANT: ClassVar[str] = "urn:ietf:params:oauth:grant-type:jwt-bearer"

    token_endpoint: str
    client_id: str
    user: str
    private_key_pem: Optional[PrivateKeySecret] = Field(default=None, repr=False)
    private_key_jwk: Optional[Mapping[str, Any]] = Field(default=None, repr=False)
    aud: Optional[str] = None
    scope: Optional[str] = None
    jwt_lifetime_seconds: int = Field(default=180, ge=1)
    cache_ttl_seconds: Optional[int] = Field(default=None, ge=1)
    cache_skew_seconds: int = Field(default=30, ge=0)
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )

    type: Literal["SalesforceOAuth20AppClient"] = "SalesforceOAuth20AppClient"

    _token_cache: Optional[Tuple[Dict[str, Any], float]] = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:
        if not self.private_key_jwk and not self.private_key_pem:
            raise ValueError(
                "private key (PEM or JWK) required for Salesforce JWT bearer flow"
            )

    def _audience_value(self) -> str:
        if self.aud:
            return self.aud.rstrip("/")
        base, _, _ = self.token_endpoint.partition("/services/")
        candidate = base or self.token_endpoint
        return candidate.split("?")[0].rstrip("/")

    def _private_key_value(self) -> Mapping[str, Any] | str | bytes:
        if self.private_key_jwk:
            return dict(self.private_key_jwk)
        if isinstance(self.private_key_pem, SecretStr):
            return self.private_key_pem.get_secret_value()
        if isinstance(self.private_key_pem, SecretBytes):
            return self.private_key_pem.get_secret_value()
        raise ValueError(
            "private key (PEM or JWK) required for Salesforce JWT bearer flow"
        )

    def _effective_scope(self, scope: Optional[str]) -> Optional[str]:
        return scope if scope is not None else self.scope

    def _jwt_assertion(self) -> str:
        now = int(time.time())
        payload = {
            "iss": self.client_id,
            "sub": self.user,
            "aud": self._audience_value(),
            "iat": now,
            "exp": now + self.jwt_lifetime_seconds,
        }
        key = self._private_key_value()
        return jwt.encode(payload, key=key, algorithm="RS256")

    async def _request_token(self, scope: Optional[str]) -> Dict[str, Any]:
        form = {
            "grant_type": self.JWT_GRANT,
            "assertion": self._jwt_assertion(),
        }
        effective_scope = self._effective_scope(scope)
        if effective_scope:
            form["scope"] = effective_scope
        async with self.http_client_factory() as client:
            response = await client.post_retry(
                self.token_endpoint,
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def access_token_payload(self, scope: Optional[str] = None) -> Dict[str, Any]:
        now = time.time()
        if self.cache_ttl_seconds and self._token_cache:
            cached_payload, expires_at = self._token_cache
            if now < expires_at - self.cache_skew_seconds:
                return dict(cached_payload)

        payload = dict(await self._request_token(scope))
        if "access_token" not in payload:
            raise ValueError("access_token missing from Salesforce response")

        if self.cache_ttl_seconds:
            expiry = now + self.cache_ttl_seconds
            self._token_cache = (dict(payload), expiry)

        return payload

    async def access_token(self, scope: Optional[str] = None) -> str:
        payload = await self.access_token_payload(scope=scope)
        token = payload.get("access_token")
        if not isinstance(token, str):
            raise ValueError("access_token missing from Salesforce response")
        return token


__all__ = ["SalesforceOAuth20AppClient"]
