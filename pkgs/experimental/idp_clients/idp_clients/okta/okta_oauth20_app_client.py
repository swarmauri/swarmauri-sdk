from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from idp_clients.base.oauth20_app_client import OAuth20AppClient

@dataclass(frozen=True)
class OktaOAuth20AppClient:
    """OAuth 2.0 client-credentials for Okta.

    token_url is derived from the issuer: {issuer}/v1/token
    e.g. issuer=https://example.okta.com/oauth2/default
    """
    issuer: str
    client_id: str
    client_secret: str

    async def access_token(self, scope: Optional[str] = None) -> str:
        token_url = f"{self.issuer.rstrip('/')}/v1/token"
        client = OAuth20AppClient(token_url, self.client_id, self.client_secret)
        return await client.access_token(scope)
