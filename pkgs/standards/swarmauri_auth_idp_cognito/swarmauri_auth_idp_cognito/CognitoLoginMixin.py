"""Shared helpers for Cognito login implementations."""

from __future__ import annotations

import json
from typing import Any, Callable, Mapping, Optional

import jwt
from pydantic import ConfigDict

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


# ID-token signing algorithms accepted by this implementation.
#
# Amazon Cognito user pools sign ID tokens with RS256 only (RSA signature
# with SHA-256):
# https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-id-token.html
#
# This allowlist is owned by the implementation. It must never be built
# from the token's unverified ``alg`` header: a token that claims any other
# algorithm (including ``none``) is rejected before verification. Client
# secret signing (e.g. SECRET_HASH) is a separate concern and is not
# governed by this list.
ID_TOKEN_ALGORITHMS: tuple[str, ...] = ("RS256",)


class CognitoLoginMixin:
    """Provide shared discovery, HTTP, and state helpers for Cognito logins."""

    model_config = ConfigDict(extra="forbid")

    _http_client_factory: Callable[[], RetryingAsyncClient]
    _discovery: Mapping[str, Any] | None

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
            response = await client.post_retry(
                url, data=data, headers=request_headers
            )
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
        algorithm = header.get("alg")
        if not algorithm:
            raise ValueError("missing alg in id_token header")
        if algorithm not in ID_TOKEN_ALGORITHMS:
            raise ValueError(f"unsupported id_token signing algorithm: {algorithm}")
        jwks = await self._http_get(jwks_uri)
        signer = _load_signing_key(jwks, kid)
        return jwt.decode(
            id_token,
            signer,
            algorithms=list(ID_TOKEN_ALGORITHMS),
            audience=expected_audience,
            issuer=issuer,
        )


__all__ = ["CognitoLoginMixin"]
