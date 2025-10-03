from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

OAUTH2_SCOPES = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
AUTH_EP = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_EP = "https://oauth2.googleapis.com/token"
USERINFO = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"

@dataclass(frozen=True)
class GoogleOAuth20Login:
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes

    async def auth_url(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self.state_secret, {"verifier": verifier})
        url = (f"{AUTH_EP}?response_type=code&client_id={self.client_id}"
               f"&redirect_uri={self.redirect_uri}&scope={OAUTH2_SCOPES}"
               f"&state={state}&code_challenge={challenge}"
               f"&code_challenge_method=S256&access_type=offline&prompt=select_account")
        return {"url": url, "state": state}

    async def exchange_and_userinfo(self, code: str, state: str) -> Dict[str, Any]:
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
            tok = (await c.post_retry(TOKEN_EP, data=form, headers={"Accept":"application/json"})).json()
            hdr = {"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/json"}
            ui  = (await c.get_retry(USERINFO, headers=hdr)).json()
        return {"issuer":"google-oauth2", "sub": ui.get("id"), "email": ui.get("email"), "name": ui.get("name"),
                "raw": {"tokens": tok, "userinfo": ui}}
