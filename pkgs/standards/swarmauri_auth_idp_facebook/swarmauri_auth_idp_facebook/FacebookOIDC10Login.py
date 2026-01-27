"""Facebook OpenID Connect 1.0 login implementation."""

from __future__ import annotations

import json
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


def _select_signing_key(jwks: Mapping[str, Any], kid: str) -> Any:
    for entry in jwks.get("keys", []):
        if entry.get("kid") == kid:
            serialized = json.dumps(entry)
            kty = entry.get("kty", "RSA").upper()
            if kty == "EC":
                return jwt.algorithms.ECAlgorithm.from_jwk(serialized)
            return jwt.algorithms.RSAAlgorithm.from_jwk(serialized)
    raise ValueError("signing key not found")


@ComponentBase.register_type(OIDC10LoginBase, "FacebookOIDC10Login")
class FacebookOIDC10Login(OIDC10LoginBase):
    """Facebook confidential client OpenID Connect 1.0 login."""

    model_config = ConfigDict(extra="forbid")

    issuer: str = Field(default="https://www.facebook.com")
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: bytes
    scope: str = Field(default="openid email public_profile")

    type: Literal["FacebookOIDC10Login"] = "FacebookOIDC10Login"

    _discovery: Optional[Mapping[str, Any]] = PrivateAttr(default=None)
    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )

    def _state_secret(self) -> bytes:
        return self.state_secret

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _discovery_url(self) -> str:
        return f"{self.issuer.rstrip('/')}/.well-known/openid-configuration"

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
        state = sign_state(self._state_secret(), {"verifier": verifier})
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
        issuer: str,
    ) -> Mapping[str, Any]:
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("kid missing from id_token header")
        signer = _select_signing_key(jwks, kid)
        alg = header.get("alg", "RS256")
        return jwt.decode(
            id_token,
            signer,
            algorithms=[alg],
            audience=self.client_id,
            issuer=issuer,
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
        if not id_token:
            raise ValueError("no id_token in response")
        jwks = await self._jwks(metadata["jwks_uri"])
        claims = self._decode_id_token(
            id_token,
            jwks=jwks,
            issuer=metadata.get("issuer", self.issuer),
        )
        email = claims.get("email")
        name = claims.get("name") or claims.get("given_name")
        if (not email or not name) and metadata.get("userinfo_endpoint"):
            async with self._http_client_factory() as client:
                response = await client.get_retry(
                    metadata["userinfo_endpoint"],
                    headers={
                        "Authorization": f"Bearer {tokens.get('access_token', '')}",
                        "Accept": "application/json",
                    },
                )
                response.raise_for_status()
                userinfo = response.json()
            email = email or userinfo.get("email")
            name = name or userinfo.get("name")
        return {
            "issuer": "facebook-oidc10",
            "tokens": tokens,
            "claims": claims,
            "sub": claims.get("sub"),
            "email": email,
            "name": name,
        }


__all__ = ["FacebookOIDC10Login"]
