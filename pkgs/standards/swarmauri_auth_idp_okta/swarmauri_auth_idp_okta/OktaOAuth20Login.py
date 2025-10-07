"""Okta OAuth 2.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20LoginBase

from .OktaOAuthLoginMixin import OktaOAuthLoginMixin


@ComponentBase.register_type(OAuth20LoginBase, "OktaOAuth20Login")
class OktaOAuth20Login(OktaOAuthLoginMixin, OAuth20LoginBase):
    """Implement the Okta OAuth 2.0 Authorization Code flow with PKCE."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        profile = await self._fetch_userinfo(tokens["access_token"])
        subject = (
            profile.get("sub")
            or profile.get("uid")
            or profile.get("sub_id")
            or profile.get("id")
        )
        return {
            "issuer": "okta-oauth20",
            "sub": subject,
            "email": profile.get("email"),
            "name": profile.get("name") or profile.get("given_name"),
            "raw": {"tokens": tokens, "userinfo": profile},
        }
