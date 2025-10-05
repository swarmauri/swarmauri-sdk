from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

@dataclass(frozen=True)
class KeycloakOAuth20Login:
    """OAuth 2.0 Authorization Code + PKCE for Keycloak (uses UserInfo for identity)."""
    issuer: str
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes
    scope: str = "openid email profile"

    async def _disc(self) -> Dict[str, Any]:
        url = f"{self.issuer.rstrip('/')}/.well-known/openid-configuration"
        async with RetryingAsyncClient() as c:
            r = await c.get_retry(url, headers={"Accept":"application/json"})
            r.raise_for_status()
            return r.json()

    async def auth_url(self) -> Dict[str, str]:
        d = await self._disc()
        verifier, challenge = make_pkce_pair()
        state = sign_state(self.state_secret, {"verifier": verifier})
        url = (f'{d["authorization_endpoint"]}?response_type=code'
               f'&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
               f'&scope={self.scope}&state={state}'
               f'&code_challenge={challenge}&code_challenge_method=S256')
        return {"url": url, "state": state}

    async def exchange_and_userinfo(self, code: str, state: str) -> Dict[str, Any]:
        s = verify_state(self.state_secret, state)
        d = await self._disc()
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code_verifier": s["verifier"],
        }
        async with RetryingAsyncClient() as c:
            tok = (await c.post_retry(d["token_endpoint"], data=form, headers={"Accept":"application/json"})).json()
            hdr = {"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/json"}
            ui  = (await c.get_retry(d["userinfo_endpoint"], headers=hdr)).json()
        return {"issuer":"keycloak-oauth2", "sub": ui.get("sub"),
                "email": ui.get("email"), "name": ui.get("name") or ui.get("given_name"),
                "raw": {"tokens": tok, "userinfo": ui}}
