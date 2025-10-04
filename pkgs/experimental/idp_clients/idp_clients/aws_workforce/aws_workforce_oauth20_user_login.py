from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import time
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

@dataclass(frozen=True)
class AwsWorkforceOAuth20Login:
    authorization_endpoint: str
    token_endpoint: str
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes
    scope: str = "openid aws sso:account:access"

    async def auth_url(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self.state_secret, {"verifier": verifier, "ts": int(time.time())})
        url = (f"{self.authorization_endpoint}?response_type=code"
               f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
               f"&scope={self.scope}&state={state}"
               f"&code_challenge={challenge}&code_challenge_method=S256")
        return {"url": url, "state": state}

    async def exchange(self, code: str, state: str) -> Dict[str, Any]:
        s = verify_state(self.state_secret, state)
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code_verifier": s["verifier"],
        }
        async with RetryingAsyncClient() as c:
            r = await c.post_retry(self.token_endpoint, data=form, headers={"Accept":"application/json"})
            r.raise_for_status()
            tok = r.json()
        return {"issuer": "aws-workforce", "tokens": tok}
