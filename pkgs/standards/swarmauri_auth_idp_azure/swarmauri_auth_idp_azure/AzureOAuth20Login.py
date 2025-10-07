"""Azure Active Directory OAuth 2.0 Authorization Code login."""

from __future__ import annotations

from typing import Any, Literal, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20LoginBase

from .AzureLoginMixin import AzureLoginMixin


@ComponentBase.register_type(OAuth20LoginBase, "AzureOAuth20Login")
class AzureOAuth20Login(AzureLoginMixin, OAuth20LoginBase):
    """Implement the Azure AD OAuth 2.0 authorization code flow."""

    type: Literal["AzureOAuth20Login"] = "AzureOAuth20Login"

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        access_token = tokens.get("access_token")
        profile: Mapping[str, Any] = {}
        if access_token:
            profile = await self._fetch_profile(access_token)
        email = (
            profile.get("mail") or profile.get("userPrincipalName") if profile else None
        )
        name = profile.get("displayName") if profile else None
        return {
            "issuer": "azure-oauth20",
            "tokens": tokens,
            "profile": profile,
            "sub": profile.get("id") if profile else None,
            "email": email,
            "name": name,
        }


__all__ = ["AzureOAuth20Login"]
