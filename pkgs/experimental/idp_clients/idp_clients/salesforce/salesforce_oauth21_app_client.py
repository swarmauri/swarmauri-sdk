from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .salesforce_oauth20_app_client import SalesforceOAuth20AppClient

@dataclass(frozen=True)
class SalesforceOAuth21AppClient:
    \"\"OAuth 2.1-aligned server-to-server client for Salesforce.
    Uses the JWT bearer flow under the hood but enforces modern constraints in your caller.
    \"\"
    token_endpoint: str
    client_id: str
    user: str
    private_key_jwk: Dict[str, Any]    # prefer JWK for KMS-backed keys
    aud: Optional[str] = None

    async def access_token(self, *, expires_in: int = 180) -> Dict[str, Any]:
        impl = SalesforceOAuth20AppClient(
            token_endpoint=self.token_endpoint,
            client_id=self.client_id,
            user=self.user,
            private_key_jwk=self.private_key_jwk,
            aud=self.aud,
        )
        return await impl.access_token(expires_in=expires_in)
