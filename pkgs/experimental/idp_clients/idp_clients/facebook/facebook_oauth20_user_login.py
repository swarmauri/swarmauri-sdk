from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

@dataclass(frozen=True)
class FacebookOAuth20Login:
    """OAuth 2.0 Authorization Code + PKCE for Facebook; identity via Graph /me."""
    auth_base: str = "https://www.facebook.com/v19.0"
    graph_base: str = "https://graph.facebook.com/v19.0"
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    state_secret: bytes = b""
    scope: str = "email public_profile"

    def _auth_ep(self) -> str: return f"{self.auth_base.rstrip('/')}/dialog/oauth"
    def _token_ep(self) -> str: return f"{self.graph_base.rstrip('/')}/oauth/access_token"

    async def auth_url(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self.state_secret, {"verifier": verifier})
        url = (f'{self._auth_ep()}?response_type=code'
               f'&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
               f'&scope={self.scope}&state={state}'
               f'&code_challenge={challenge}&code_challenge_method=S256')
        return {"url": url, "state": state}

    async def exchange_and_profile(self, code: str, state: str) -> Dict[str, Any]:
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
            tok = (await c.post_retry(self._token_ep(), data=form, headers={"Accept":"application/json"})).json()
            hdr = {"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/json"}
            me  = (await c.get_retry(f'{self.graph_base.rstrip("/")}/me?fields=id,name,email', headers=hdr)).json()
        return {"issuer":"facebook-oauth2", "sub": str(me.get("id")), "email": me.get("email"), "name": me.get("name"),
                "raw":{"tokens": tok, "user": me}}
