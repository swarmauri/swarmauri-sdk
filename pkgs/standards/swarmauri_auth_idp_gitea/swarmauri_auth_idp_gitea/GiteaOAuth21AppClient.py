"""Gitea OAuth 2.1 client credentials app client implementation."""

from __future__ import annotations

import json
import time
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

import jwt
from pydantic import ConfigDict, Field, PrivateAttr, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.auth_idp import OAuth21AppClientBase
from swarmauri_base.auth_idp.http import RetryingAsyncClient


@ComponentBase.register_type(OAuth21AppClientBase, "GiteaOAuth21AppClient")
class GiteaOAuth21AppClient(OAuth21AppClientBase):
    """Request OAuth 2.1 tokens from Gitea using secrets or JWT assertions."""

    model_config = ConfigDict(extra="forbid")

    base_url: str
    client_id: str
    client_secret: Optional[SecretStr] = None
    private_key_jwk: Optional[Dict[str, Any]] = None
    cache_skew_seconds: int = Field(default=30, ge=0)

    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )
    _cached_token: Optional[Tuple[str, float]] = PrivateAttr(default=None)

    def _token_endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}/login/oauth/access_token"

    def _client_secret_value(self) -> Optional[str]:
        return self.client_secret.get_secret_value() if self.client_secret else None

    @staticmethod
    def _load_private_key(jwk_payload: Mapping[str, Any], algorithm: str) -> Any:
        serialized = json.dumps(jwk_payload)
        if algorithm.upper().startswith("ES"):
            return jwt.algorithms.ECAlgorithm.from_jwk(serialized)
        return jwt.algorithms.RSAAlgorithm.from_jwk(serialized)

    def _client_assertion_body(self) -> Dict[str, str]:
        if not self.private_key_jwk:
            return {}
        algorithm = self.private_key_jwk.get("alg", "RS256")
        key = self._load_private_key(self.private_key_jwk, algorithm)
        now = int(time.time())
        payload = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": self._token_endpoint(),
            "iat": now,
            "exp": now + 300,
            "jti": str(now),
        }
        headers: Dict[str, str] = {}
        if kid := self.private_key_jwk.get("kid"):
            headers["kid"] = kid
        assertion = jwt.encode(
            payload, key=key, algorithm=algorithm, headers=headers or None
        )
        return {
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
        }

    async def _fetch_token(self, scope: Optional[str]) -> Tuple[str, float]:
        form = {"grant_type": "client_credentials"}
        if scope:
            form["scope"] = scope
        body = self._client_assertion_body()
        auth = None
        if body:
            form["client_id"] = self.client_id
        else:
            secret = self._client_secret_value()
            if not secret:
                raise ValueError("client_secret or private_key_jwk must be provided")
            auth = (self.client_id, secret)
        payload = {**form, **body}
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                self._token_endpoint(),
                data=payload,
                auth=auth,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
        expires_at = time.time() + int(data.get("expires_in", 3600))
        return data["access_token"], expires_at

    async def access_token(self, scope: Optional[str] = None) -> str:
        cached = self._cached_token
        now = time.time()
        if cached and now < cached[1] - self.cache_skew_seconds:
            return cached[0]
        token, expires_at = await self._fetch_token(scope)
        self._cached_token = (token, expires_at)
        return token
