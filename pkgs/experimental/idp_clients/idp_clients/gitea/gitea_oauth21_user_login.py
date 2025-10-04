from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

@dataclass(frozen=True)
class GiteaOAuth21Login:
    """OAuth 2.1-aligned Authorization Code + PKCE for Gitea.
    Uses REST API to fetch identity (no ID token dependency).
    """
    base_url: str                   # e.g., https://gitea.example.com
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes
    scope: str = "read:user"        # minimal scope for /api/v1/user
    api_base: str | None = None     # defaults to {base_url}/api/v1

    def _api_base(self) -> str:
        return self.api_base or f"{self.base_url.rstrip('/')}/api/v1"

    def _auth_ep(self) -> str:
        return f"{self.base_url.rstrip('/')}/login/oauth/authorize"

    def _token_ep(self) -> str:
        return f"{self.base_url.rstrip('/')}/login/oauth/access_token"

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
            # fallback to /user/emails if needed
            email = me.get("email")
            if not email:
                try:
                    emails = (await c.get_retry(f'{self._api_base()}/user/emails', headers=hdr)).json()
                    if isinstance(emails, list) and emails:
                        primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)
                        email = (primary or emails[0]).get("email")
                except Exception:
                    pass
        name = me.get("full_name") or me.get("username") or me.get("login")
        return {"issuer":"gitea-oauth21", "sub": str(me.get("id")), "email": email, "name": name,
                "raw":{"tokens": tok, "user": me}}
