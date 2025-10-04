from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from idp_clients.base.oidc10_app_client import OIDC10AppClient

@dataclass(frozen=True)
class GiteaOIDC10AppClient:
    """OIDC discovery-driven client-credentials for Gitea (if OIDC provider is enabled).

    issuer: your Gitea issuer, e.g., https://gitea.example.com (or realm issuer if configured)
    """
    issuer: str
    client_id: str
    client_secret: str

    async def access_token(self, scope: Optional[str] = None) -> str:
        client = OIDC10AppClient(self.issuer, self.client_id, self.client_secret)
        return await client.access_token(scope)
