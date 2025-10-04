from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from idp_clients.base.oauth20_app_client import OAuth20AppClient

@dataclass(frozen=True)
class GitLabOAuth20AppClient:
    \"\"OAuth 2.0 client-credentials for GitLab.

    token_url is derived from base_url: {base_url}/oauth/token
    \"\"
    base_url: str
    client_id: str
    client_secret: str

    async def access_token(self, scope: Optional[str] = None) -> str:
        token_url = f\"{self.base_url.rstrip('/')}/oauth/token\"
        client = OAuth20AppClient(token_url, self.client_id, self.client_secret)
        return await client.access_token(scope)
