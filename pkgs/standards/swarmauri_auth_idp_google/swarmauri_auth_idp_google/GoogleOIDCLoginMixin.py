"""Shared helpers for Google OAuth 2.1 / OIDC user login implementations."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Sequence

import jwt
from pydantic import ConfigDict, Field, SecretBytes, SecretStr

from swarmauri_base.auth_idp import (
    RetryingAsyncClient,
    make_nonce,
    make_pkce_pair,
    sign_state,
    verify_state,
)

GOOGLE_DISCOVERY_ENDPOINT = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
DEFAULT_ALLOWED_ISSUERS = (
    "https://accounts.google.com",
    "accounts.google.com",
)


class GoogleOIDCLoginMixin:
    """Discovery, PKCE, and ID token validation utilities for Google logins."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: SecretBytes
    scope: str = Field(default="openid email profile")
    allowed_issuers: Sequence[str] = Field(
        default=DEFAULT_ALLOWED_ISSUERS, exclude=True, repr=False
    )
    discovery_endpoint: str = Field(
        default=GOOGLE_DISCOVERY_ENDPOINT, exclude=True, repr=False
    )
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )
    discovery_cache: Optional[Mapping[str, Any]] = Field(
        default=None, exclude=True, repr=False
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret_value(self) -> bytes:
        return self.state_secret.get_secret_value()

    async def _metadata(self) -> Mapping[str, Any]:
        if self.discovery_cache is None:
            async with self.http_client_factory() as client:
                response = await client.get_retry(
                    self.discovery_endpoint, headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                self.discovery_cache = response.json()
        return self.discovery_cache

    async def _auth_payload(self) -> Mapping[str, str]:
        metadata = await self._metadata()
        verifier, challenge = make_pkce_pair()
        nonce = make_nonce()
        state = sign_state(
            self._state_secret_value(), {"verifier": verifier, "nonce": nonce}
        )
        endpoint = metadata["authorization_endpoint"]
        url = (
            f"{endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}&nonce={nonce}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
            f"&include_granted_scopes=true&prompt=select_account"
        )
        return {"url": url, "state": state, "verifier": verifier, "nonce": nonce}

    async def _exchange_tokens(self, code: str, state: str) -> Mapping[str, Any]:
        payload = verify_state(self._state_secret_value(), state)
        metadata = await self._metadata()
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self._client_secret_value(),
            "code_verifier": payload["verifier"],
        }
        async with self.http_client_factory() as client:
            response = await client.post_retry(
                metadata["token_endpoint"],
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            tokens = response.json()
            jwks_response = await client.get_retry(
                metadata["jwks_uri"], headers={"Accept": "application/json"}
            )
            jwks_response.raise_for_status()
            jwks = jwks_response.json()
        claims = await self._decode_id_token(tokens, jwks, metadata)
        if claims.get("nonce") != payload["nonce"]:
            raise ValueError("nonce mismatch")
        if metadata.get("userinfo_endpoint"):
            if not claims.get("email") or not claims.get("name"):
                async with self.http_client_factory() as client:
                    userinfo_response = await client.get_retry(
                        metadata["userinfo_endpoint"],
                        headers={
                            "Authorization": f"Bearer {tokens['access_token']}",
                            "Accept": "application/json",
                        },
                    )
                    userinfo_response.raise_for_status()
                    userinfo = userinfo_response.json()
                claims = {**userinfo, **claims}
        return {"tokens": tokens, "claims": claims}

    async def _decode_id_token(
        self,
        tokens: Mapping[str, Any],
        jwks: Mapping[str, Any],
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        id_token = tokens.get("id_token")
        if not id_token:
            raise ValueError("no id_token in response")
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("missing kid in id_token header")
        key_entry = next(
            (entry for entry in jwks.get("keys", []) if entry.get("kid") == kid),
            None,
        )
        if not key_entry:
            raise ValueError("signing key not found")
        algorithm = header.get("alg", "RS256")
        signer = jwt.algorithms.RSAAlgorithm.from_jwk(key_entry)
        issuers = list(self.allowed_issuers)
        issuer_from_metadata = metadata.get("issuer")
        if issuer_from_metadata and issuer_from_metadata not in issuers:
            issuers.append(issuer_from_metadata)
        return jwt.decode(
            id_token,
            signer,
            algorithms=[algorithm],
            audience=self.client_id,
            issuer=issuers,
        )


__all__ = ["GoogleOIDCLoginMixin"]
