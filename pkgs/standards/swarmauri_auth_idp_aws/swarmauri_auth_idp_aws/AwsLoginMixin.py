"""Shared helpers for AWS OAuth login implementations."""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping

from pydantic import ConfigDict, Field, PrivateAttr, SecretStr

from swarmauri_base.auth_idp import (
    RetryingAsyncClient,
    make_pkce_pair,
    sign_state,
    verify_state,
)


class AwsLoginMixin:
    """Common PKCE/state/token helpers shared across AWS logins."""

    model_config = ConfigDict(extra="forbid")

    authorization_endpoint: str
    token_endpoint: str
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: bytes
    scope: str = Field(default="openid aws sso:account:access")

    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret(self) -> bytes:
        return self.state_secret

    async def _auth_payload(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret(), {"verifier": verifier})
        url = (
            f"{self.authorization_endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state, "verifier": verifier}

    async def _post_token(self, form: Mapping[str, Any]) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                self.token_endpoint,
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
        }
        return await self._post_token(form)


__all__ = [
    "AwsLoginMixin",
    "RetryingAsyncClient",
    "make_pkce_pair",
    "sign_state",
    "verify_state",
]
