"""Facebook OAuth 2.1 Authorization Code login."""

from __future__ import annotations

from typing import Any, Literal, Mapping, Optional

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase

from .FacebookLoginMixin import FacebookLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "FacebookOAuth21Login")
class FacebookOAuth21Login(FacebookLoginMixin, OAuth21LoginBase):
    """Implement the Facebook OAuth 2.1 authorization code flow."""

    type: Literal["FacebookOAuth21Login"] = "FacebookOAuth21Login"

    async def auth_url(self) -> Mapping[str, str]:
        payload = await self._auth_payload()
        return {"url": payload["url"], "state": payload["state"]}

    async def _claims_from_id_token(
        self, id_token: Optional[str]
    ) -> Optional[Mapping[str, Any]]:
        if not id_token:
            return None
        try:
            claims = await self._decode_id_token(id_token)
        except ValueError:
            return None
        return claims

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        tokens = await self._exchange_tokens(code, state)
        claims = await self._claims_from_id_token(tokens.get("id_token"))
        if claims:
            return {
                "issuer": "facebook-oauth21",
                "tokens": tokens,
                "claims": claims,
                "sub": claims.get("sub"),
                "email": claims.get("email"),
                "name": claims.get("name") or claims.get("given_name"),
            }
        access_token = tokens.get("access_token")
        profile: Mapping[str, Any] = {}
        if access_token:
            profile = await self._fetch_profile(access_token)
        sub = str(profile.get("id")) if profile.get("id") is not None else None
        return {
            "issuer": "facebook-oauth21",
            "tokens": tokens,
            "profile": profile,
            "sub": sub,
            "email": profile.get("email") if profile else None,
            "name": profile.get("name") if profile else None,
        }


__all__ = ["FacebookOAuth21Login"]
