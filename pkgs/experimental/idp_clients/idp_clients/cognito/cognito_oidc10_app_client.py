from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from idp_clients.base.oidc10_app_client import OIDC10AppClient

@dataclass(frozen=True)
class CognitoOIDC10AppClient:
    """OIDC discovery-driven client-credentials for AWS Cognito User Pools.

    issuer may be either:
      - The pool issuer: https://cognito-idp.<region>.amazonaws.com/<userPoolId>
      - Your custom domain: https://<yourdomain>.auth.<region>.amazoncognito.com
    """
    issuer: str
    client_id: str
    client_secret: str

    async def access_token(self, scope: Optional[str] = None) -> str:
        client = OIDC10AppClient(self.issuer, self.client_id, self.client_secret)
        return await client.access_token(scope)
