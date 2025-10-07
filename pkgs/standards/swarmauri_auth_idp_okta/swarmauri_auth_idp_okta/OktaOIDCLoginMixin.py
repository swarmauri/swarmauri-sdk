"""Shared helpers for Okta OIDC-based login implementations."""

from __future__ import annotations

from typing import Any, Mapping

import jwt

from .OktaOAuthLoginMixin import OktaOAuthLoginMixin


class OktaOIDCLoginMixin(OktaOAuthLoginMixin):
    """Augment the Okta OAuth mixin with ID token validation."""

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
        async with self.http_client_factory() as client:
            response = await client.get_retry(
                metadata["jwks_uri"], headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            jwks = response.json()
        key_entry = next(
            (entry for entry in jwks.get("keys", []) if entry.get("kid") == kid),
            None,
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
            issuer=self.issuer,
        )


__all__ = ["OktaOIDCLoginMixin"]
