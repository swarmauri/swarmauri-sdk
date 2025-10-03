from __future__ import annotations
import time, jwt
from dataclasses import dataclass
from typing import Optional, Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient

JWT_GRANT = "urn:ietf:params:oauth:grant-type:jwt-bearer"

@dataclass(frozen=True)
class SalesforceOAuth20AppClient:
    \"\"Server-to-server OAuth 2.0 for Salesforce using the **JWT bearer** flow (RFC 7523).
    Requires a Connected App with JWT enabled; the subject user must have access.
    token_endpoint: e.g., https://login.salesforce.com/services/oauth2/token (or your My Domain)
    aud: must match the login host (e.g., https://login.salesforce.com, https://test.salesforce.com, or https://<my>.my.salesforce.com).
    \"\"
    token_endpoint: str
    client_id: str                     # Connected App consumer key
    user: str                          # Salesforce username (subject)
    private_key_pem: Optional[bytes] = None
    private_key_jwk: Optional[Dict[str, Any]] = None
    aud: Optional[str] = None          # audience (login host)

    async def access_token(self, *, expires_in: int = 180) -> Dict[str, Any]:
        now = int(time.time())
        aud = self.aud or self.token_endpoint.split("/services/")[0]
        key = self.private_key_jwk or self.private_key_pem
        if key is None:
            raise ValueError("private key (PEM or JWK) required for JWT bearer")
        assertion = jwt.encode(
            { "iss": self.client_id, "sub": self.user, "aud": aud, "iat": now, "exp": now + expires_in },
            key=key, algorithm="RS256"
        )
        form = { "grant_type": JWT_GRANT, "assertion": assertion }
        async with RetryingAsyncClient() as c:
            r = await c.post_retry(self.token_endpoint, data=form, headers={"Accept": "application/json"})
            r.raise_for_status()
            return r.json()             # includes access_token, instance_url, id, token_type, issued_at
