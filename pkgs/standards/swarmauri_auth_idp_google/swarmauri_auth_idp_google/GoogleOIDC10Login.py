"""Google OpenID Connect 1.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OIDC10LoginBase

from .GoogleOIDCLoginMixin import GoogleOIDCLoginMixin


@ComponentBase.register_type(OIDC10LoginBase, "GoogleOIDC10Login")
class GoogleOIDC10Login(GoogleOIDCLoginMixin, OIDC10LoginBase):
    """Implement Google OIDC 1.0 Authorization Code flow with PKCE."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange(self, code: str, state: str) -> Mapping[str, Any]:
        result = await self._exchange_tokens(code, state)
        tokens = result["tokens"]
        claims = result["claims"]
        return {
            "issuer": "google-oidc",
            "sub": claims.get("sub"),
            "email": claims.get("email"),
            "name": claims.get("name") or claims.get("given_name"),
            "raw": {"tokens": tokens, "claims": claims},
        }
