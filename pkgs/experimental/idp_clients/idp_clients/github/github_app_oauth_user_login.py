from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import httpx
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

@dataclass(frozen=True)
class GitHubAppOAuthLogin:
    client_id: str
    client_secret: str
    redirect_uri: str
    oauth_base: str = "https://github.com/login/oauth"
    api_base: str = "https://api.github.com"

    def auth_url(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(b"CHANGE_ME_SECRET", {"code_verifier": verifier})  # inject your HMAC secret at call site
        url = (f"{self.oauth_base}/authorize?client_id={self.client_id}"
               f"&redirect_uri={self.redirect_uri}"
               f"&state={state}&code_challenge={challenge}"
               f"&code_challenge_method=S256")
        return {"url": url, "state": state, "code_verifier": verifier}

    async def exchange_code(self, code: str, state: str, code_verifier: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{self.oauth_base}/access_token",
                             data={"client_id": self.client_id,
                                   "client_secret": self.client_secret,
                                   "code": code,
                                   "redirect_uri": self.redirect_uri,
                                   "code_verifier": code_verifier},
                             headers={"Accept": "application/json"})
            r.raise_for_status()
            tok = r.json()
        return tok

    async def fetch_min_profile(self, access_token: str) -> Dict[str, Any]:
        hdr = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"}
        async with httpx.AsyncClient(timeout=30) as c:
            u = (await c.get(f"{self.api_base}/user", headers=hdr)).json()
            emails = (await c.get(f"{self.api_base}/user/emails", headers=hdr)).json()
        primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
        return {"issuer": "github-app", "sub": str(u["id"]), "name": u.get("name") or u["login"], "email": primary}
