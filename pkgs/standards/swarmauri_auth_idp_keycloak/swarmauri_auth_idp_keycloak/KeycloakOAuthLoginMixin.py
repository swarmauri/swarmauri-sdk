"""Shared helpers for Keycloak OAuth user login implementations."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from pydantic import ConfigDict, Field, SecretBytes, SecretStr

from swarmauri_base.auth_idp import (
    RetryingAsyncClient,
    make_pkce_pair,
    sign_state,
    verify_state,
)


class KeycloakOAuthLoginMixin:
    """Reusable PKCE, discovery, and UserInfo helpers for Keycloak logins."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    issuer: str
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: SecretBytes
    scope: str = Field(default="openid email profile")
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )
    discovery_cache: Optional[Mapping[str, Any]] = Field(
        default=None, exclude=True, repr=False
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret_value(self) -> bytes:
        return self.state_secret.get_secret_value()

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

    async def _auth_payload(self) -> Mapping[str, str]:
        metadata = await self._metadata()
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret_value(), {"verifier": verifier})
        endpoint = metadata["authorization_endpoint"]
        url = (
            f"{endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state, "verifier": verifier}

    async def _exchange_tokens(self, code: str, state: str) -> Mapping[str, Any]:
        payload = verify_state(self._state_secret_value(), state)
        metadata = await self._metadata()
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self._client_secret_value(),
            "code_verifier": payload["verifier"],
        }
        async with self.http_client_factory() as client:
            response = await client.post_retry(
                metadata["token_endpoint"],
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _fetch_userinfo(self, access_token: str) -> Mapping[str, Any]:
        metadata = await self._metadata()
        endpoint = metadata.get("userinfo_endpoint")
        if not endpoint:
            return {}
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        async with self.http_client_factory() as client:
            response = await client.get_retry(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()


__all__ = ["KeycloakOAuthLoginMixin"]
