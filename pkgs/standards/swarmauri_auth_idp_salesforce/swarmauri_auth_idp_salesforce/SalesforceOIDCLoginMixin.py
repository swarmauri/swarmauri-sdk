"""Shared helpers for Salesforce OIDC-based login implementations."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import jwt

from .SalesforceOAuthLoginMixin import SalesforceOAuthLoginMixin


class SalesforceOIDCLoginMixin(SalesforceOAuthLoginMixin):
    """Extend the Salesforce OAuth mixin with discovery and ID token verification."""

    discovery_cache: Optional[Mapping[str, Any]] = None

    DISCOVERY_PATH = "/.well-known/openid-configuration"

    async def _metadata(self) -> Mapping[str, Any]:  # type: ignore[override]
        if self.discovery_cache is None:
            url = f"{self.base_url.rstrip('/')}{self.DISCOVERY_PATH}"
            async with self.http_client_factory() as client:
                response = await client.get_retry(
                    url, headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                self.discovery_cache = response.json()
        return self.discovery_cache

    def _authorization_endpoint(self) -> str:  # type: ignore[override]
        metadata = self.discovery_cache
        if metadata and metadata.get("authorization_endpoint"):
            return metadata["authorization_endpoint"]
        return super()._authorization_endpoint()

    def _token_endpoint(self) -> str:  # type: ignore[override]
        metadata = self.discovery_cache
        if metadata and metadata.get("token_endpoint"):
            return metadata["token_endpoint"]
        return super()._token_endpoint()

    def _userinfo_endpoint(self) -> str:  # type: ignore[override]
        metadata = self.discovery_cache
        if metadata and metadata.get("userinfo_endpoint"):
            return metadata["userinfo_endpoint"]
        return super()._userinfo_endpoint()

    async def _decode_id_token(
        self,
        tokens: Mapping[str, Any],
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        id_token = tokens.get("id_token")
        if not id_token:
            raise ValueError("no id_token in response")
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("missing kid in id_token header")
        jwks_uri = metadata.get("jwks_uri")
        if not jwks_uri:
            raise ValueError("no jwks_uri in discovery metadata")
        async with self.http_client_factory() as client:
            response = await client.get_retry(
                jwks_uri, headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            jwks = response.json()
        key_entry = next(
            (entry for entry in jwks.get("keys", []) if entry.get("kid") == kid), None
        )
        if not key_entry:
            raise ValueError("signing key not found")
        algorithm = header.get("alg", "RS256")
        signer = jwt.algorithms.RSAAlgorithm.from_jwk(key_entry)
        return jwt.decode(
            id_token,
            signer,
            algorithms=[algorithm],
            audience=self.client_id,
            issuer=metadata.get("issuer", self.base_url),
        )


__all__ = ["SalesforceOIDCLoginMixin"]
