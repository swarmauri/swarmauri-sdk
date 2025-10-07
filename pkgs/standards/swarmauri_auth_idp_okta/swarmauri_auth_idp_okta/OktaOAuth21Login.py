"""Okta OAuth 2.1 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase

from .OktaOIDCLoginMixin import OktaOIDCLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "OktaOAuth21Login")
class OktaOAuth21Login(OktaOIDCLoginMixin, OAuth21LoginBase):
    """Implement the Okta OAuth 2.1 Authorization Code flow with PKCE."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        metadata = await self._metadata()
        claims = await self._decode_id_token(tokens, metadata)
        return {
            "issuer": "okta-oauth21",
            "sub": claims["sub"],
            "email": claims.get("email"),
            "name": claims.get("name") or claims.get("preferred_username") or "Unknown",
            "raw": {"tokens": tokens, "claims": claims},
        }
