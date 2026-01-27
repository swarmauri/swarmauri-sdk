"""Keycloak OpenID Connect 1.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OIDC10LoginBase

from .KeycloakOIDCLoginMixin import KeycloakOIDCLoginMixin


@ComponentBase.register_type(OIDC10LoginBase, "KeycloakOIDC10Login")
class KeycloakOIDC10Login(KeycloakOIDCLoginMixin, OIDC10LoginBase):
    """Implement OIDC 1.0 Authorization Code with PKCE for Keycloak."""

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def exchange(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        metadata = await self._metadata()
        claims = await self._decode_id_token(tokens, metadata)
        email = claims.get("email")
        name = claims.get("name") or claims.get("preferred_username") or "Unknown"
        if (not email or name == "Unknown") and metadata.get("userinfo_endpoint"):
            profile = await self._fetch_userinfo(tokens["access_token"])
            email = profile.get("email") or email
            name = profile.get("name") or profile.get("given_name") or name
        return {
            "issuer": "keycloak-oidc",
            "sub": claims["sub"],
            "email": email,
            "name": name,
            "raw": {"tokens": tokens, "claims": claims},
        }
