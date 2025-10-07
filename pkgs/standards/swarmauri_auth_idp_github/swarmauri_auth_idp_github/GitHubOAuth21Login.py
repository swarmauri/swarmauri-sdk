"""GitHub OAuth 2.1 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase

from .GitHubOAuthLoginMixin import GitHubOAuthLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "GitHubOAuth21Login")
class GitHubOAuth21Login(GitHubOAuthLoginMixin, OAuth21LoginBase):
    """Implement the GitHub OAuth 2.1 Authorization Code flow with PKCE."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        profile = await self._fetch_profile(tokens["access_token"])
        return {
            "issuer": "github-oauth21",
            "sub": str(profile.get("id")),
            "email": profile.get("email"),
            "name": profile.get("name") or profile.get("login"),
            "raw": {"tokens": tokens, "user": profile},
        }
