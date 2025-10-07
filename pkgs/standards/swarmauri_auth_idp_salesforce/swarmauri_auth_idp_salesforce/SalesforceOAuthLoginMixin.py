"""Shared helpers for Salesforce OAuth user login implementations."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from pydantic import ConfigDict, Field, SecretBytes, SecretStr

from swarmauri_base.auth_idp import (
    RetryingAsyncClient,
    make_pkce_pair,
    sign_state,
    verify_state,
)


class SalesforceOAuthLoginMixin:
    """Reusable PKCE, token exchange, and profile helpers for Salesforce logins."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    base_url: str
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: SecretBytes
    scope: str = Field(default="refresh_token")
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )

    AUTH_PATH: str = Field(
        default="/services/oauth2/authorize", exclude=True, repr=False
    )
    TOKEN_PATH: str = Field(default="/services/oauth2/token", exclude=True, repr=False)
    USERINFO_PATH: str = Field(
        default="/services/oauth2/userinfo", exclude=True, repr=False
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret_value(self) -> bytes:
        return self.state_secret.get_secret_value()

    def _authorization_endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.AUTH_PATH}"

    def _token_endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.TOKEN_PATH}"

    def _userinfo_endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.USERINFO_PATH}"

    async def _auth_payload(self) -> Mapping[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret_value(), {"verifier": verifier})
        url = (
            f"{self._authorization_endpoint()}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state, "verifier": verifier}

    async def _exchange_tokens(self, code: str, state: str) -> Mapping[str, Any]:
        payload = verify_state(self._state_secret_value(), state)
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
                self._token_endpoint(),
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _fetch_userinfo(self, access_token: str) -> Mapping[str, Any]:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        async with self.http_client_factory() as client:
            response = await client.get_retry(
                self._userinfo_endpoint(), headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def _fetch_identity_profile(
        self, identity_url: Optional[str], access_token: str
    ) -> Mapping[str, Any]:
        if not identity_url:
            return {}
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        async with self.http_client_factory() as client:
            response = await client.get_retry(identity_url, headers=headers)
            response.raise_for_status()
            return response.json()


__all__ = ["SalesforceOAuthLoginMixin"]
