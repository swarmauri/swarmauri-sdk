"""Shared helpers for Google OAuth 2.0 style user login implementations."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from pydantic import ConfigDict, Field, SecretBytes, SecretStr

from swarmauri_base.auth_idp import (
    RetryingAsyncClient,
    make_pkce_pair,
    sign_state,
    verify_state,
)

GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
GOOGLE_DEFAULT_SCOPE = (
    "https://www.googleapis.com/auth/userinfo.email "
    "https://www.googleapis.com/auth/userinfo.profile"
)


class GoogleOAuthLoginMixin:
    """Reusable PKCE/state/token helpers shared across Google OAuth logins."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: SecretBytes
    scope: str = Field(default=GOOGLE_DEFAULT_SCOPE)
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret_value(self) -> bytes:
        return self.state_secret.get_secret_value()

    async def _auth_payload(self) -> Mapping[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret_value(), {"verifier": verifier})
        url = (
            f"{GOOGLE_AUTHORIZATION_ENDPOINT}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
            f"&access_type=offline&prompt=select_account"
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
                GOOGLE_TOKEN_ENDPOINT,
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _fetch_profile(self, access_token: str) -> Mapping[str, Any]:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        async with self.http_client_factory() as client:
            response = await client.get_retry(GOOGLE_USERINFO_ENDPOINT, headers=headers)
            response.raise_for_status()
            return response.json()


__all__ = ["GoogleOAuthLoginMixin"]
