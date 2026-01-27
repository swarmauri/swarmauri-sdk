"""Salesforce OpenID Connect 1.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OIDC10LoginBase

from .SalesforceOIDCLoginMixin import SalesforceOIDCLoginMixin


@ComponentBase.register_type(OIDC10LoginBase, "SalesforceOIDC10Login")
class SalesforceOIDC10Login(SalesforceOIDCLoginMixin, OIDC10LoginBase):
    """Implement Salesforce OIDC 1.0 Authorization Code flow with PKCE."""

    async def auth_url(self) -> Mapping[str, str]:
        metadata = await self._metadata()
        self.discovery_cache = metadata
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange(self, code: str, state: str) -> Mapping[str, Any]:
        metadata = await self._metadata()
        self.discovery_cache = metadata
        tokens = await self._exchange_tokens(code, state)
        claims = await self._decode_id_token(tokens, metadata)
        email = claims.get("email")
        name = claims.get("name") or claims.get("preferred_username") or "Unknown"
        if (not email or name == "Unknown") and metadata.get("userinfo_endpoint"):
            profile = await self._fetch_userinfo(tokens["access_token"])
            email = email or profile.get("email")
            name = (
                name
                if name != "Unknown"
                else profile.get("name")
                or profile.get("preferred_username")
                or "Unknown"
            )
        return {
            "issuer": "salesforce-oidc",
            "sub": claims["sub"],
            "email": email,
            "name": name,
            "raw": {"tokens": tokens, "claims": claims},
        }
