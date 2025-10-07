"""Cognito OAuth 2.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from pydantic import Field, SecretBytes, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth20LoginBase, make_pkce_pair, sign_state

from .CognitoLoginMixin import CognitoLoginMixin


@ComponentBase.register_type(OAuth20LoginBase, "CognitoOAuth20Login")
class CognitoOAuth20Login(CognitoLoginMixin, OAuth20LoginBase):
    """AWS Cognito OAuth 2.0 Authorization Code flow with PKCE."""

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
        access_token = token_json["access_token"]
        userinfo_endpoint = metadata.get("userinfo_endpoint") or (
            f"{self.issuer.rstrip('/')}/oauth2/userInfo"
        )
        userinfo_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        userinfo_json = await self._http_get(
            userinfo_endpoint, headers=userinfo_headers
        )
        name = (
            userinfo_json.get("name")
            or userinfo_json.get("given_name")
            or "Unknown"
        )
        return {
            "issuer": "cognito-oauth2",
            "sub": userinfo_json.get("sub"),
            "email": userinfo_json.get("email"),
            "name": name,
            "raw": {"tokens": token_json, "userinfo": userinfo_json},
        }
