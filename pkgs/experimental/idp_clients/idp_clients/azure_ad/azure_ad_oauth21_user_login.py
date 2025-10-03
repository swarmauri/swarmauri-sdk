from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state
import time

GRAPH_SCOPE = "User.Read offline_access"
GRAPH_ME = "https://graph.microsoft.com/v1.0/me"

@dataclass(frozen=True)
class AzureOAuth21Login:
    tenant: str
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes

    async def _endpoints(self) -> Dict[str, str]:
        base = f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0"
        return {"auth": base + "/authorize", "token": base + "/token"}

    async def auth_url(self) -> Dict[str, str]:
        ep = await self._endpoints()
        verifier, challenge = make_pkce_pair()
        state = sign_state(self.state_secret, {"pkce_verifier": verifier, "ts": int(time.time())})
        url = (f'{ep["auth"]}?response_type=code'
               f'&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
               f'&scope={GRAPH_SCOPE}&state={state}'
               f'&code_challenge={challenge}&code_challenge_method=S256&prompt=select_account')
        return {"url": url, "state": state}

    async def exchange_and_profile(self, code: str, state: str) -> Dict[str, Any]:
        s = verify_state(self.state_secret, state)
        ep = await self._endpoints()
        form = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code_verifier": s["pkce_verifier"],
            "code": code,
            "scope": GRAPH_SCOPE
        }
        async with RetryingAsyncClient() as c:
            tok = (await c.post_retry(ep["token"], data=form, headers={"Accept":"application/json"})).json()
            hdr = {"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/json"}
            me  = (await c.get_retry(GRAPH_ME, headers=hdr)).json()
        email = me.get("mail") or me.get("userPrincipalName")
        return {"issuer":"azure-oauth21", "sub": me["id"], "email": email, "name": me.get("displayName"),
                "raw":{"tokens": tok, "me": me}}
