from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from idp_clients.base.oidc10_app_client import OIDC10AppClient

@dataclass(frozen=True)
class KeycloakOIDC10AppClient:
    """OIDC discovery-driven client-credentials for Keycloak.

    issuer: Keycloak realm issuer, e.g. https://kc.example.com/realms/myrealm
    """
    issuer: str
    client_id: str
    client_secret: str

    async def access_token(self, scope: Optional[str] = None) -> str:
        client = OIDC10AppClient(self.issuer, self.client_id, self.client_secret)
        return await client.access_token(scope)
