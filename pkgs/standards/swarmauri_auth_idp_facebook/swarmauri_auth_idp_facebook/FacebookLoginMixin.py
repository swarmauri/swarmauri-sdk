"""Shared helpers for Facebook login implementations."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Mapping

import jwt
from pydantic import ConfigDict, Field, PrivateAttr, SecretStr

from swarmauri_base.auth_idp import (
    RetryingAsyncClient,
    make_pkce_pair,
    sign_state,
    verify_state,
)

_DEFAULT_AUTH_BASE = "https://www.facebook.com/v19.0"
_DEFAULT_GRAPH_BASE = "https://graph.facebook.com/v19.0"
_GRAPH_FIELDS = "id,name,email"
_JWKS_URI = "https://www.facebook.com/.well-known/oauth/openid/jwks/"


def _load_signing_key(jwks: Mapping[str, Any], kid: str) -> Any:
    """Select the signing key referenced by *kid*."""

    for entry in jwks.get("keys", []):
        if entry.get("kid") == kid:
            serialized = json.dumps(entry)
            kty = entry.get("kty", "RSA").upper()
            if kty == "EC":
                return jwt.algorithms.ECAlgorithm.from_jwk(serialized)
            return jwt.algorithms.RSAAlgorithm.from_jwk(serialized)
    raise ValueError("signing key not found")


class FacebookLoginMixin:
    """Common helpers shared across Facebook OAuth/OIDC login flows."""

    model_config = ConfigDict(extra="forbid")

    auth_base: str = Field(default=_DEFAULT_AUTH_BASE)
    graph_base: str = Field(default=_DEFAULT_GRAPH_BASE)
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: bytes
    scope: str = Field(default="email public_profile")

    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )

    def _authorization_endpoint(self) -> str:
        return f"{self.auth_base.rstrip('/')}/dialog/oauth"

    def _token_endpoint(self) -> str:
        return f"{self.graph_base.rstrip('/')}/oauth/access_token"

    def _graph_me_endpoint(self) -> str:
        return f"{self.graph_base.rstrip('/')}/me?fields={_GRAPH_FIELDS}"

    def _jwks_uri(self) -> str:
        return _JWKS_URI

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret(self) -> bytes:
        return self.state_secret

    async def _auth_payload(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret(), {"verifier": verifier})
        url = (
            f"{self._authorization_endpoint()}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state, "verifier": verifier}

    async def _post_token(self, form: Mapping[str, Any]) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                self._token_endpoint(),
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _exchange_tokens(self, code: str, state: str) -> Mapping[str, Any]:
        payload = verify_state(self._state_secret(), state)
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self._client_secret_value(),
            "code_verifier": payload["verifier"],
        }
        return await self._post_token(form)

    async def _fetch_profile(self, access_token: str) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.get_retry(
                self._graph_me_endpoint(),
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
            return response.json()

    async def _jwks(self) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.get_retry(
                self._jwks_uri(),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _decode_id_token(self, id_token: str) -> Mapping[str, Any]:
        jwks = await self._jwks()
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("missing kid in id_token header")
        signer = _load_signing_key(jwks, kid)
        algorithm = header.get("alg", "RS256")
        return jwt.decode(
            id_token,
            signer,
            algorithms=[algorithm],
            audience=self.client_id,
            issuer="https://www.facebook.com",
        )


__all__ = ["FacebookLoginMixin"]
