"""Gitea OAuth 2.1 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase

from .GiteaOAuthLoginMixin import GiteaOAuthLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "GiteaOAuth21Login")
class GiteaOAuth21Login(GiteaOAuthLoginMixin, OAuth21LoginBase):
    """Implement OAuth 2.1 Authorization Code with PKCE for Gitea."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        profile = await self._fetch_profile(tokens["access_token"])
        name = (
            profile.get("full_name") or profile.get("username") or profile.get("login")
        )
        return {
            "issuer": "gitea-oauth21",
            "sub": str(profile.get("id")),
            "email": profile.get("email"),
            "name": name,
            "raw": {"tokens": tokens, "user": profile},
        }
