"""Salesforce OAuth 2.1 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase

from .SalesforceOIDCLoginMixin import SalesforceOIDCLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "SalesforceOAuth21Login")
class SalesforceOAuth21Login(SalesforceOIDCLoginMixin, OAuth21LoginBase):
    """Implement the Salesforce OAuth 2.1 Authorization Code flow with PKCE."""

    async def auth_url(self) -> Mapping[str, str]:
        metadata = await self._metadata()
        # Update endpoints based on discovery for auth_url usage
        self.discovery_cache = metadata
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        metadata = await self._metadata()
        self.discovery_cache = metadata
        tokens = await self._exchange_tokens(code, state)
        claims = {}
        try:
            claims = await self._decode_id_token(tokens, metadata)
        except Exception:
            claims = {}
        email = claims.get("email")
        name = claims.get("name") or claims.get("preferred_username") or "Unknown"
        subject = claims.get("sub")
        if (not email or not subject) and metadata.get("userinfo_endpoint"):
            profile = await self._fetch_userinfo(tokens["access_token"])
            email = email or profile.get("email")
            name = (
                name
                if name != "Unknown"
                else profile.get("name")
                or profile.get("preferred_username")
                or "Unknown"
            )
            subject = subject or profile.get("sub") or profile.get("user_id")
        return {
            "issuer": "salesforce-oauth21",
            "sub": subject,
            "email": email,
            "name": name,
            "raw": {"tokens": tokens, "claims": claims},
        }
