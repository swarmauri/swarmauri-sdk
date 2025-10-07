"""Azure Active Directory OpenID Connect 1.0 login implementation."""

from __future__ import annotations

from typing import Any, Callable, Literal, Mapping, Optional

import jwt
from pydantic import ConfigDict, Field, PrivateAttr, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import (
    OIDC10LoginBase,
    RetryingAsyncClient,
    make_pkce_pair,
    sign_state,
    verify_state,
)


@ComponentBase.register_type(OIDC10LoginBase, "AzureOIDC10Login")
class AzureOIDC10Login(OIDC10LoginBase):
    """Azure AD confidential client OIDC login using authorization code + PKCE."""

    model_config = ConfigDict(extra="forbid")

    tenant: str
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: bytes
    scope: str = Field(default="openid profile email")

    type: Literal["AzureOIDC10Login"] = "AzureOIDC10Login"

    _discovery: Optional[Mapping[str, Any]] = PrivateAttr(default=None)
    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )

    def _discovery_url(self) -> str:
        return (
            f"https://login.microsoftonline.com/{self.tenant}/v2.0/.well-known"
            "/openid-configuration"
        )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret(self) -> bytes:
        return self.state_secret

    async def _metadata(self) -> Mapping[str, Any]:
        if self._discovery is None:
            async with self._http_client_factory() as client:
                response = await client.get_retry(
                    self._discovery_url(),
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                self._discovery = response.json()
        return self._discovery

    async def auth_url(self) -> Mapping[str, str]:
        metadata = await self._metadata()
        verifier, challenge = make_pkce_pair()
        state = sign_state(
            self._state_secret(),
            {"verifier": verifier},
        )
        endpoint = metadata["authorization_endpoint"]
        url = (
            f"{endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state}

    async def _token_request(
        self, endpoint: str, form: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                endpoint,
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _jwks(self, url: str) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.get_retry(
                url,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    def _decode_id_token(
        self,
        id_token: str,
        *,
        jwks: Mapping[str, Any],
        expected_issuer: str,
    ) -> Mapping[str, Any]:
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("kid missing from id_token header")
        key = next(
            (entry for entry in jwks.get("keys", []) if entry.get("kid") == kid), None
        )
        if key is None:
            raise ValueError("signing key not found for id_token")
        alg = header.get("alg", "RS256")
        signer = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        return jwt.decode(
            id_token,
            signer,
            algorithms=[alg],
            audience=self.client_id,
            issuer=expected_issuer,
        )

    async def exchange(self, code: str, state: str) -> Mapping[str, Any]:
        metadata = await self._metadata()
        payload = verify_state(self._state_secret(), state)
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self._client_secret_value(),
            "code_verifier": payload["verifier"],
        }
        tokens = await self._token_request(metadata["token_endpoint"], form)
        id_token = tokens.get("id_token")
        claims: Mapping[str, Any] = {}
        if id_token:
            jwks = await self._jwks(metadata["jwks_uri"])
            claims = self._decode_id_token(
                id_token,
                jwks=jwks,
                expected_issuer=metadata["issuer"],
            )
        email = (
            claims.get("email") or claims.get("preferred_username") if claims else None
        )
        name = claims.get("name") or claims.get("given_name") if claims else None
        return {
            "issuer": "azure-oidc10",
            "tokens": tokens,
            "claims": claims,
            "sub": claims.get("sub") if claims else None,
            "email": email,
            "name": name,
        }


__all__ = ["AzureOIDC10Login"]
