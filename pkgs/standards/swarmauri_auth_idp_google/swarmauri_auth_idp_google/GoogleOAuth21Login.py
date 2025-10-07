"""Google OAuth 2.1 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase

from .GoogleOIDCLoginMixin import GoogleOIDCLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "GoogleOAuth21Login")
class GoogleOAuth21Login(GoogleOIDCLoginMixin, OAuth21LoginBase):
    """Implement the Google OAuth 2.1 Authorization Code flow with PKCE."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        result = await self._exchange_tokens(code, state)
        tokens = result["tokens"]
        claims = result["claims"]
        return {
            "issuer": "google-oauth21",
            "sub": claims.get("sub"),
            "email": claims.get("email"),
            "name": claims.get("name") or claims.get("given_name"),
            "raw": {"tokens": tokens, "claims": claims},
        }
