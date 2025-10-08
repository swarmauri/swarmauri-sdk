"""Cognito OpenID Connect 1.0 Authorization Code login implementation."""

from __future__ import annotations

from typing import Any, Mapping

from pydantic import Field, SecretBytes, SecretStr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OIDC10LoginBase, make_pkce_pair, sign_state

from .CognitoLoginMixin import CognitoLoginMixin


@ComponentBase.register_type(OIDC10LoginBase, "CognitoOIDC10Login")
class CognitoOIDC10Login(CognitoLoginMixin, OIDC10LoginBase):
    """AWS Cognito OIDC 1.0 Authorization Code flow with ID token validation."""

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

    async def exchange(self, code: str, state: str) -> Mapping[str, Any]:
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
        email = claims.get("email")
        name = claims.get("name") or claims.get("given_name") or "Unknown"
        if (not email or name == "Unknown") and metadata.get("userinfo_endpoint"):
            headers = {
                "Authorization": f"Bearer {token_json['access_token']}",
                "Accept": "application/json",
            }
            userinfo_json = await self._http_get(
                metadata["userinfo_endpoint"], headers=headers
            )
            email = userinfo_json.get("email") or email
            name = userinfo_json.get("name") or name
        return {
            "issuer": "cognito-oidc",
            "sub": claims["sub"],
            "email": email,
            "name": name,
            "raw": {"tokens": token_json},
        }
