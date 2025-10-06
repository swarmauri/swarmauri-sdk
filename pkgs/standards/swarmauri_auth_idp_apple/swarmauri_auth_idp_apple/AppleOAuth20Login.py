"""Apple OAuth 2.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Literal, Mapping

from pydantic import Field, SecretBytes

from swarmauri_base.auth_idp import OAuth20LoginBase

from .internal import AppleLoginMixin, make_nonce, make_pkce_pair, sign_state


class AppleOAuth20Login(AppleLoginMixin, OAuth20LoginBase):
    """Apple OAuth 2.0 Authorization Code flow with PKCE."""

    type: Literal["AppleOAuth20Login"] = "AppleOAuth20Login"

    team_id: str
    key_id: str
    client_id: str
    private_key_pem: SecretBytes
    redirect_uri: str
    state_secret: SecretBytes
    scope: str = Field(default="name email")
    authorization_endpoint: str = Field(
        default="https://appleid.apple.com/auth/authorize", frozen=True
    )
    token_endpoint: str = Field(
        default="https://appleid.apple.com/auth/token", frozen=True
    )
    jwks_uri: str = Field(default="https://appleid.apple.com/auth/keys", frozen=True)

    async def auth_url(self) -> Mapping[str, str]:
        verifier, challenge = make_pkce_pair()
        nonce = make_nonce()
        state = sign_state(self._state_secret(), {"verifier": verifier, "nonce": nonce})
        url = (
            f"{self.authorization_endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}&nonce={nonce}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state}

    async def exchange_and_identity(self, code: str, state: str) -> Mapping[str, Any]:
        payload = self._state_payload(state)
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self._client_secret(),
            "code_verifier": payload["verifier"],
        }
        token_json = await self._http_post(self.token_endpoint, data=form)
        claims = await self._decode_identity(
            token_json.get("id_token"),
            nonce=payload["nonce"],
            jwks_uri=self.jwks_uri,
            expected_audience=self.client_id,
        )
        return {
            "issuer": "apple-oauth2",
            "sub": claims["sub"],
            "email": claims.get("email"),
            "name": claims.get("name"),
        }
