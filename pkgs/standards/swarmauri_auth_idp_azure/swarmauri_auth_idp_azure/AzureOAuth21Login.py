"""Azure Active Directory OAuth 2.1 Authorization Code login."""

from __future__ import annotations

from typing import Any, Literal, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase

from .AzureLoginMixin import AzureLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "AzureOAuth21Login")
class AzureOAuth21Login(AzureLoginMixin, OAuth21LoginBase):
    """Implement the Azure AD OAuth 2.1 authorization code flow."""

    type: Literal["AzureOAuth21Login"] = "AzureOAuth21Login"

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload(prompt="select_account")
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
            "issuer": "azure-oauth21",
            "tokens": tokens,
            "profile": profile,
            "sub": profile.get("id") if profile else None,
            "email": email,
            "name": name,
        }


__all__ = ["AzureOAuth21Login"]
