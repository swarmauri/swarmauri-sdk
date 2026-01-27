"""Salesforce OAuth 2.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20LoginBase

from .SalesforceOAuthLoginMixin import SalesforceOAuthLoginMixin


@ComponentBase.register_type(OAuth20LoginBase, "SalesforceOAuth20Login")
class SalesforceOAuth20Login(SalesforceOAuthLoginMixin, OAuth20LoginBase):
    """Implement the Salesforce OAuth 2.0 Authorization Code flow with PKCE."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        profile = {}
        try:
            profile = await self._fetch_userinfo(tokens["access_token"])
        except Exception:  # pragma: no cover - fallback to identity endpoint
            profile = {}
        if not profile:
            identity = await self._fetch_identity_profile(
                tokens.get("id"), tokens["access_token"]
            )
        else:
            identity = profile
        subject = (
            profile.get("sub")
            or profile.get("user_id")
            or identity.get("user_id")
            or identity.get("id")
        )
        email = profile.get("email") or identity.get("email")
        name = (
            profile.get("name")
            or identity.get("display_name")
            or identity.get("preferred_username")
            or identity.get("username")
            or "Unknown"
        )
        return {
            "issuer": "salesforce-oauth20",
            "sub": subject,
            "email": email,
            "name": name,
            "raw": {"tokens": tokens, "userinfo": profile, "identity": identity},
        }
