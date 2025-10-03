from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import httpx
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

@dataclass(frozen=True)
class GitHubOAuthLogin:
    client_id: str
    client_secret: str
    redirect_uri: str
    oauth_base: str = "https://github.com/login/oauth"
    api_base: str = "https://api.github.com"

    def auth_url(self, state_secret: bytes, scopes: str = "read:user user:email") -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(state_secret, {"code_verifier": verifier})
        url = (f"{self.oauth_base}/authorize?client_id={self.client_id}"
               f"&redirect_uri={self.redirect_uri}&scope={scopes}"
               f"&state={state}&code_challenge={challenge}&code_challenge_method=S256")
        return {"url": url, "state": state}

    async def exchange_and_profile(self, code: str, state: str, state_secret: bytes) -> Dict[str, Any]:
        s = verify_state(state_secret, state)
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{self.oauth_base}/access_token",
                             data={"client_id": self.client_id,
                                   "client_secret": self.client_secret,
                                   "code": code,
                                   "redirect_uri": self.redirect_uri,
                                   "code_verifier": s["code_verifier"]},
                             headers={"Accept": "application/json"})
            r.raise_for_status()
            tok = r.json()
            hdr = {"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/vnd.github+json"}
            u = (await c.get(f"{self.api_base}/user", headers=hdr)).json()
            emails = (await c.get(f"{self.api_base}/user/emails", headers=hdr)).json()
        primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
        return {"issuer":"github-oauth", "sub": str(u["id"]), "email": primary, "name": u.get("name") or u["login"], "raw":{"tokens": tok}}
