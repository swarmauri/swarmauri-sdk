"""Shared helpers for Azure Active Directory OAuth login implementations."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Mapping

from pydantic import ConfigDict, Field, PrivateAttr, SecretStr

from swarmauri_base.auth_idp import (
    RetryingAsyncClient,
    make_pkce_pair,
    sign_state,
    verify_state,
)

_DEFAULT_SCOPE = "User.Read offline_access"
_GRAPH_ME_URL = "https://graph.microsoft.com/v1.0/me"


class AzureLoginMixin:
    """Common PKCE/state/token helpers shared across Azure AD logins."""

    model_config = ConfigDict(extra="forbid")

    tenant: str
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: bytes
    scope: str = Field(default=_DEFAULT_SCOPE)
    graph_me_url: str = Field(default=_GRAPH_ME_URL, frozen=True)

    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret(self) -> bytes:
        return self.state_secret

    def _authority_base(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0"

    def _authorization_endpoint(self) -> str:
        return f"{self._authority_base()}/authorize"

    def _token_endpoint(self) -> str:
        return f"{self._authority_base()}/token"

    async def _auth_payload(self, *, prompt: str | None = None) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(
            self._state_secret(),
            {"verifier": verifier, "ts": int(time.time())},
        )
        url = (
            f"{self._authorization_endpoint()}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        if prompt:
            url = f"{url}&prompt={prompt}"
        return {"url": url, "state": state}

    async def _post_token(self, form: Mapping[str, Any]) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                self._token_endpoint(),
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _exchange_tokens(self, code: str, state: str) -> Mapping[str, Any]:
        payload = verify_state(self._state_secret(), state)
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self._client_secret_value(),
            "code_verifier": payload["verifier"],
            "scope": self.scope,
        }
        return await self._post_token(form)

    async def _fetch_profile(self, access_token: str) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.get_retry(
                self.graph_me_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
            return response.json()


__all__ = [
    "AzureLoginMixin",
]
