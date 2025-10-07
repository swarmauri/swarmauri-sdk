"""Apple OAuth 2.1 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from pydantic import Field, PrivateAttr, SecretBytes
from swarmauri_base.auth_idp import OAuth21LoginBase, make_nonce, make_pkce_pair, sign_state
from swarmauri_base.ComponentBase import ComponentBase

from .internal import (
    DISCOVERY_URL,
    AppleLoginMixin,
)


@ComponentBase.register_type(OAuth21LoginBase, "AppleOAuth21Login")
class AppleOAuth21Login(AppleLoginMixin, OAuth21LoginBase):
    """Apple OAuth 2.1 Authorization Code flow using OIDC discovery."""

    team_id: str
    key_id: str
    client_id: str
    private_key_pem: SecretBytes
    redirect_uri: str
    state_secret: SecretBytes
    scope: str = Field(default="openid email name")
    discovery_url: str = Field(default=DISCOVERY_URL, frozen=True)
    _discovery: Optional[Mapping[str, Any]] = PrivateAttr(default=None)

    async def _metadata(self) -> Mapping[str, Any]:
        if self._discovery is None:
            self._discovery = await self._http_get(self.discovery_url)
        return self._discovery

    async def auth_url(self) -> Mapping[str, str]:
        metadata = await self._metadata()
        verifier, challenge = make_pkce_pair()
        nonce = make_nonce()
        state = sign_state(self._state_secret(), {"verifier": verifier, "nonce": nonce})
        endpoint = metadata["authorization_endpoint"]
        url = (
            f"{endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}&nonce={nonce}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        payload = self._state_payload(state)
        metadata = await self._metadata()
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self._client_secret(),
            "code_verifier": payload["verifier"],
        }
        token_json = await self._http_post(metadata["token_endpoint"], data=form)
        claims = await self._decode_identity(
            token_json.get("id_token"),
            nonce=payload["nonce"],
            jwks_uri=metadata["jwks_uri"],
            expected_audience=self.client_id,
        )
        return {
            "issuer": "apple-oauth21",
            "sub": claims["sub"],
            "email": claims.get("email"),
            "name": claims.get("name"),
        }
