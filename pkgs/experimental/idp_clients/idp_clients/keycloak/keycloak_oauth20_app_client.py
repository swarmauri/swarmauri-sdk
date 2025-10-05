from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from idp_clients.base.oauth20_app_client import OAuth20AppClient

@dataclass(frozen=True)
class KeycloakOAuth20AppClient:
    """OAuth 2.0 client-credentials for Keycloak.

    token_url: {issuer}/protocol/openid-connect/token
    issuer is the realm issuer, e.g. https://kc.example.com/realms/myrealm
    """
    issuer: str
    client_id: str
    client_secret: str

    async def access_token(self, scope: Optional[str] = None) -> str:
        token_url = f"{self.issuer.rstrip('/')}/protocol/openid-connect/token"
        client = OAuth20AppClient(token_url, self.client_id, self.client_secret)
        return await client.access_token(scope)
