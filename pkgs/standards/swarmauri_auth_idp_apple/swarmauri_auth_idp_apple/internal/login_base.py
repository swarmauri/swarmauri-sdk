"""Shared helpers for Apple Sign-in login implementations."""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Optional

import jwt
from pydantic import ConfigDict, PrivateAttr

from swarmauri_base.auth_idp import RetryingAsyncClient
from swarmauri_base.auth_idp.utils import verify_state

APPLE_ISSUER = "https://appleid.apple.com"
DISCOVERY_URL = "https://appleid.apple.com/.well-known/openid-configuration"


def _load_signing_key(jwks: Mapping[str, Any], kid: str) -> Any:
    """Select the verification key referenced by the JWT header."""

    for entry in jwks.get("keys", []):
        if entry.get("kid") == kid:
            if entry.get("kty") == "EC":
                return jwt.algorithms.ECAlgorithm.from_jwk(entry)
            return jwt.algorithms.RSAAlgorithm.from_jwk(entry)
    raise ValueError("signing key not found")


class AppleLoginMixin:
    """Common behaviour shared by Apple login flows."""

    model_config = ConfigDict(extra="forbid")
    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )

    def _client_secret(self) -> str:
        private_key = self.private_key_pem.get_secret_value()
        from .client_secret import (
            AppleClientSecretFactory,
        )  # local import to avoid cycle

        return AppleClientSecretFactory(
            team_id=self.team_id,
            key_id=self.key_id,
            client_id=self.client_id,
            private_key_pem=private_key,
        ).build()

    def _state_secret(self) -> bytes:
        return self.state_secret.get_secret_value()

    def _state_payload(self, state: str) -> Dict[str, Any]:
        return verify_state(self._state_secret(), state)

    async def _http_get(self, url: str) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.get_retry(
                url, headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()

    async def _http_post(
        self, url: str, *, data: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                url, data=data, headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()

    async def _decode_identity(
        self,
        id_token: Optional[str],
        *,
        nonce: str,
        jwks_uri: str,
        expected_audience: str,
    ) -> Mapping[str, Any]:
        if not id_token:
            raise ValueError("no id_token in response")
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("missing kid in id_token header")
        jwks = await self._http_get(jwks_uri)
        signer = _load_signing_key(jwks, kid)
        alg = header.get("alg", "ES256")
        claims = jwt.decode(
            id_token,
            signer,
            algorithms=[alg],
            audience=expected_audience,
            issuer=APPLE_ISSUER,
        )
        if claims.get("nonce") != nonce:
            raise ValueError("nonce mismatch")
        return claims
