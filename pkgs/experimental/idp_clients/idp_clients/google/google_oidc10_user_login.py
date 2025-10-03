from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import jwt
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, make_nonce, sign_state, verify_state

DISCOVERY = "https://accounts.google.com/.well-known/openid-configuration"
ALLOWED_ISSUERS = {"https://accounts.google.com", "accounts.google.com"}

@dataclass(frozen=True)
class GoogleOIDC10Login:
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes
    scope: str = "openid email profile"

    async def _discover(self) -> Dict[str, Any]:
        async with RetryingAsyncClient() as c:
            r = await c.get_retry(DISCOVERY, headers={"Accept": "application/json"})
            r.raise_for_status()
            return r.json()

    async def auth_url(self) -> Dict[str, str]:
        disc = await self._discover()
        verifier, challenge = make_pkce_pair()
        nonce = make_nonce()
        state = sign_state(self.state_secret, {"verifier": verifier, "nonce": nonce})
        url = (f'{disc["authorization_endpoint"]}?response_type=code'
               f'&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
               f'&scope={self.scope}&state={state}'
               f'&nonce={nonce}&code_challenge={challenge}&code_challenge_method=S256'
               f'&include_granted_scopes=true&prompt=select_account')
        return {"url": url, "state": state}

    async def exchange(self, code: str, state: str) -> Dict[str, Any]:
        s = verify_state(self.state_secret, state)
        disc = await self._discover()
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code_verifier": s["verifier"],
        }
        async with RetryingAsyncClient() as c:
            tok = (await c.post_retry(disc["token_endpoint"], data=form,
                                      headers={"Accept": "application/json"})).json()
            jwks = (await c.get_retry(disc["jwks_uri"], headers={"Accept": "application/json"})).json()
        idt = tok.get("id_token")
        if not idt:
            raise ValueError("no id_token in response")
        header = jwt.get_unverified_header(idt)
        key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
        if not key:
            raise ValueError("signing key not found")
        pub = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        claims = jwt.decode(
            idt, pub, algorithms=[header.get("alg", "RS256")],
            audience=self.client_id, issuer=ALLOWED_ISSUERS
        )
        if claims.get("nonce") != s["nonce"]:
            raise ValueError("nonce mismatch")
        name  = claims.get("name") or "Unknown"
        email = claims.get("email")
        if not email and disc.get("userinfo_endpoint"):
            async with RetryingAsyncClient() as c2:
                ui = (await c2.get_retry(disc["userinfo_endpoint"],
                      headers={"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/json"})).json()
            email = ui.get("email") or email
            name  = ui.get("name") or name
        return {"issuer":"google-oidc", "sub": claims["sub"], "email": email, "name": name, "raw": {"tokens": tok}}
