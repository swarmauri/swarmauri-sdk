from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from idp_clients.base.oauth21_app_client import OAuth21AppClient

@dataclass(frozen=True)
class GiteaOAuth21AppClient:
    """OAuth 2.1-aligned client-credentials for Gitea (supports private_key_jwt).

    token_url is {base_url}/login/oauth/access_token.
    """
    base_url: str
    client_id: str
    client_secret: Optional[str] = None
    private_key_jwk: Optional[Dict[str, Any]] = None

    async def access_token(self, scope: Optional[str] = None) -> str:
        token_url = f"{self.base_url.rstrip('/')}/login/oauth/access_token"
        client = OAuth21AppClient(
            token_url=token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            private_key_jwk=self.private_key_jwk,
        )
        return await client.access_token(scope)
