"""Shared helpers for GitHub OAuth user login implementations."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from pydantic import ConfigDict, Field, SecretBytes, SecretStr

from swarmauri_base.auth_idp import (
    RetryingAsyncClient,
    make_pkce_pair,
    sign_state,
    verify_state,
)


class GitHubOAuthLoginMixin:
    """Reusable PKCE, token exchange, and profile helpers for GitHub logins."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: SecretBytes
    scope: str = Field(default="read:user user:email")
    oauth_base: str = Field(default="https://github.com/login/oauth")
    api_base: str = Field(default="https://api.github.com")
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret_value(self) -> bytes:
        return self.state_secret.get_secret_value()

    def _authorization_endpoint(self) -> str:
        return f"{self.oauth_base.rstrip('/')}/authorize"

    def _token_endpoint(self) -> str:
        return f"{self.oauth_base.rstrip('/')}/access_token"

    def _user_endpoint(self) -> str:
        return f"{self.api_base.rstrip('/')}/user"

    def _emails_endpoint(self) -> str:
        return f"{self.api_base.rstrip('/')}/user/emails"

    async def _auth_payload(self) -> Mapping[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret_value(), {"verifier": verifier})
        url = (
            f"{self._authorization_endpoint()}?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state, "verifier": verifier}

    async def _exchange_tokens(self, code: str, state: str) -> Mapping[str, Any]:
        payload = verify_state(self._state_secret_value(), state)
        form = {
            "client_id": self.client_id,
            "client_secret": self._client_secret_value(),
            "code": code,
            "redirect_uri": self.redirect_uri,
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

    async def _fetch_profile(self, access_token: str) -> Mapping[str, Any]:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }
        async with self.http_client_factory() as client:
            user_response = await client.get_retry(
                self._user_endpoint(), headers=headers
            )
            user_response.raise_for_status()
            profile = user_response.json()
            email = profile.get("email")
            if not email:
                try:
                    emails_response = await client.get_retry(
                        self._emails_endpoint(), headers=headers
                    )
                    emails_response.raise_for_status()
                    emails = emails_response.json()
                    if isinstance(emails, list):
                        primary = next(
                            (
                                entry
                                for entry in emails
                                if isinstance(entry, Mapping)
                                and entry.get("verified")
                                and entry.get("primary")
                            ),
                            None,
                        )
                        fallback = primary or next(
                            (entry for entry in emails if isinstance(entry, Mapping)),
                            None,
                        )
                        if fallback:
                            email = fallback.get("email")
                except Exception:  # pragma: no cover - best effort lookup
                    email = None
            if email and not profile.get("email"):
                profile["email"] = email
        return profile


__all__ = ["GitHubOAuthLoginMixin"]
