"""Google OAuth 2.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20LoginBase

from .GoogleOAuthLoginMixin import GoogleOAuthLoginMixin


@ComponentBase.register_type(OAuth20LoginBase, "GoogleOAuth20Login")
class GoogleOAuth20Login(GoogleOAuthLoginMixin, OAuth20LoginBase):
    """Implement the Google OAuth 2.0 PKCE flow with profile enrichment."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        profile = await self._fetch_profile(tokens["access_token"])
        return {
            "issuer": "google-oauth20",
            "sub": profile.get("id"),
            "email": profile.get("email"),
            "name": profile.get("name"),
            "raw": {"tokens": tokens, "userinfo": profile},
        }
