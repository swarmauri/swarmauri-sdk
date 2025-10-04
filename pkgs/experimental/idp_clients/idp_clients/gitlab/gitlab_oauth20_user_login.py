from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

@dataclass(frozen=True)
class GitLabOAuth20Login:
    \"\"OAuth 2.0 Authorization Code + PKCE for GitLab (uses GitLab API for identity).
    \"\"
    base_url: str                   # e.g., https://gitlab.com
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes
    scope: str = "read_user"        # minimal scope for /user on GitLab API
    api_base: str | None = None     # defaults to {base_url}/api/v4

    def _api_base(self) -> str:
        return self.api_base or f"{self.base_url.rstrip('/')}/api/v4"

    def _auth_ep(self) -> str:
        return f"{self.base_url.rstrip('/')}/oauth/authorize"

    def _token_ep(self) -> str:
        return f"{self.base_url.rstrip('/')}/oauth/token"

    async def auth_url(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self.state_secret, {"verifier": verifier})
        url = (f'{self._auth_ep()}?response_type=code&client_id={self.client_id}'
               f'&redirect_uri={self.redirect_uri}&scope={self.scope}'
               f'&state={state}&code_challenge={challenge}&code_challenge_method=S256')
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
            me  = (await c.get_retry(f'{self._api_base()}/user', headers=hdr)).json()
        # GitLab /user fields: id, username, name, state, avatar_url, web_url, created_at, bio, location, public_email, etc.
        email = me.get("public_email") or me.get("email")
        return {"issuer":"gitlab-oauth2", "sub": str(me.get("id")), "email": email, "name": me.get("name"),
                "raw":{"tokens": tok, "user": me}}
