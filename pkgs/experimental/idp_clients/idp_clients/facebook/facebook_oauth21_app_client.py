from __future__ import annotations
from dataclasses import dataclass
from .facebook_oauth20_app_client import FacebookOAuth20AppClient

@dataclass(frozen=True)
class FacebookOAuth21AppClient:
    """OAuth 2.1-aligned wrapper for Facebook app tokens (client_credentials)."""
    graph_base: str = "https://graph.facebook.com"
    version: str = "v19.0"
    client_id: str = ""
    client_secret: str = ""

    async def access_token(self) -> str:
        impl = FacebookOAuth20AppClient(
            graph_base=self.graph_base, version=self.version,
            client_id=self.client_id, client_secret=self.client_secret
        )
        return await impl.access_token()
