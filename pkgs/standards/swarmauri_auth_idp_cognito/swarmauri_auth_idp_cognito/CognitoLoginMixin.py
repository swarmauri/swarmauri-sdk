"""Shared helpers for Cognito login implementations."""

from __future__ import annotations

import json
from typing import Any, Callable, Mapping, Optional

import jwt
from pydantic import ConfigDict, PrivateAttr

from swarmauri_base.auth_idp.http import RetryingAsyncClient
from swarmauri_base.auth_idp.utils import verify_state


def _load_signing_key(jwks: Mapping[str, Any], kid: str) -> Any:
    """Return the cryptographic key referenced by ``kid``."""

    for entry in jwks.get("keys", []):
        if entry.get("kid") == kid:
            kty = entry.get("kty", "RSA").upper()
            serialized = json.dumps(entry)
            if kty == "EC":
                return jwt.algorithms.ECAlgorithm.from_jwk(serialized)
            return jwt.algorithms.RSAAlgorithm.from_jwk(serialized)
    raise ValueError("signing key not found")


class CognitoLoginMixin:
    """Provide shared discovery, HTTP, and state helpers for Cognito logins."""

    model_config = ConfigDict(extra="forbid")

    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )
    _discovery: Optional[Mapping[str, Any]] = PrivateAttr(default=None)

    def _state_secret_value(self) -> bytes:
        return self.state_secret.get_secret_value()

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_payload(self, state: str) -> Mapping[str, Any]:
        return verify_state(self._state_secret_value(), state)

    async def _metadata(self) -> Mapping[str, Any]:
        if self._discovery is None:
            url = f"{self.issuer.rstrip('/')}/.well-known/openid-configuration"
            self._discovery = await self._http_get(url)
        return self._discovery

    async def _http_get(
        self, url: str, *, headers: Optional[Mapping[str, str]] = None
    ) -> Mapping[str, Any]:
        request_headers = {"Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        async with self._http_client_factory() as client:
            response = await client.get_retry(url, headers=request_headers)
            response.raise_for_status()
            return response.json()

    async def _http_post(
        self,
        url: str,
        *,
        data: Mapping[str, Any],
        headers: Optional[Mapping[str, str]] = None,
    ) -> Mapping[str, Any]:
        request_headers = {"Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        async with self._http_client_factory() as client:
            response = await client.post_retry(url, data=data, headers=request_headers)
            response.raise_for_status()
            return response.json()

    async def _decode_id_token(
        self,
        id_token: Optional[str],
        *,
        jwks_uri: str,
        expected_audience: str,
        issuer: str,
    ) -> Mapping[str, Any]:
        if not id_token:
            raise ValueError("no id_token in response")
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("missing kid in id_token header")
        jwks = await self._http_get(jwks_uri)
        signer = _load_signing_key(jwks, kid)
        algorithm = header.get("alg", "RS256")
        return jwt.decode(
            id_token,
            signer,
            algorithms=[algorithm],
            audience=expected_audience,
            issuer=issuer,
        )


__all__ = ["CognitoLoginMixin"]
