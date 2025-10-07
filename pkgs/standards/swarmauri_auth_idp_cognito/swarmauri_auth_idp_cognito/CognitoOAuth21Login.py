"""Cognito OAuth 2.1 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from pydantic import Field, SecretBytes, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21LoginBase, make_pkce_pair, sign_state

from .CognitoLoginMixin import CognitoLoginMixin


@ComponentBase.register_type(OAuth21LoginBase, "CognitoOAuth21Login")
class CognitoOAuth21Login(CognitoLoginMixin, OAuth21LoginBase):
    """AWS Cognito OAuth 2.1 Authorization Code flow leveraging OIDC discovery."""

    issuer: str
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: SecretBytes
    scope: str = Field(default="openid email profile")

    async def auth_url(self) -> Mapping[str, str]:
        metadata = await self._metadata()
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret_value(), {"verifier": verifier})
        endpoint = metadata["authorization_endpoint"]
        url = (
            f"{endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
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
            "client_secret": self._client_secret_value(),
            "code_verifier": payload["verifier"],
        }
        token_json = await self._http_post(metadata["token_endpoint"], data=form)
        claims = await self._decode_id_token(
            token_json.get("id_token"),
            jwks_uri=metadata["jwks_uri"],
            expected_audience=self.client_id,
            issuer=metadata.get("issuer", self.issuer),
        )
        name = claims.get("name") or claims.get("given_name") or "Unknown"
        return {
            "issuer": "cognito-oauth21",
            "sub": claims["sub"],
            "email": claims.get("email"),
            "name": name,
            "raw": {"tokens": token_json},
        }
