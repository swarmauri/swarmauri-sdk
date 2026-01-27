"""Facebook OAuth 2.0 Authorization Code login."""

from __future__ import annotations

from typing import Any, Literal, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20LoginBase

from .FacebookLoginMixin import FacebookLoginMixin


@ComponentBase.register_type(OAuth20LoginBase, "FacebookOAuth20Login")
class FacebookOAuth20Login(FacebookLoginMixin, OAuth20LoginBase):
    """Implement the Facebook OAuth 2.0 authorization code flow."""

    type: Literal["FacebookOAuth20Login"] = "FacebookOAuth20Login"

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        access_token = tokens.get("access_token")
        profile: Mapping[str, Any] = {}
        if access_token:
            profile = await self._fetch_profile(access_token)
        sub = str(profile.get("id")) if profile.get("id") is not None else None
        return {
            "issuer": "facebook-oauth20",
            "tokens": tokens,
            "profile": profile,
            "sub": sub,
            "email": profile.get("email") if profile else None,
            "name": profile.get("name") if profile else None,
        }


__all__ = ["FacebookOAuth20Login"]
