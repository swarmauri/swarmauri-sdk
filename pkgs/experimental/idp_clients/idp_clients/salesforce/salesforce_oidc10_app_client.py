from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient
from .salesforce_oauth20_app_client import SalesforceOAuth20AppClient

DISCOVERY_SUFFIX = "/.well-known/openid-configuration"

@dataclass(frozen=True)
class SalesforceOIDC10AppClient:
    \"\"OIDC discovery-driven server-to-server client for Salesforce.
    Discovery locates the token endpoint; token acquisition still uses JWT bearer.
    \"\"
    issuer: str                         # e.g., https://login.salesforce.com or your My Domain
    client_id: str
    user: str
    private_key_pem: Optional[bytes] = None
    private_key_jwk: Optional[Dict[str, Any]] = None

    async def _discover(self) -> Dict[str, Any]:
        url = f"{self.issuer.rstrip('/')}{DISCOVERY_SUFFIX}"
        async with RetryingAsyncClient() as c:
            r = await c.get_retry(url, headers={"Accept":"application/json"})
            r.raise_for_status()
            return r.json()

    async def access_token(self, *, expires_in: int = 180) -> Dict[str, Any]:
        disc = await self._discover()
        token_endpoint = disc.get("token_endpoint") or f"{self.issuer.rstrip('/')}/services/oauth2/token"
        impl = SalesforceOAuth20AppClient(
            token_endpoint=token_endpoint,
            client_id=self.client_id,
            user=self.user,
            private_key_pem=self.private_key_pem,
            private_key_jwk=self.private_key_jwk,
            aud=self.issuer,
        )
        return await impl.access_token(expires_in=expires_in)
