from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import httpx, jwt, time
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

@dataclass(frozen=True)
class AzureOIDC10Login:
    tenant: str                      # "organizations", "common", or tenant GUID
    client_id: str
    client_secret: str               # confidential client
    redirect_uri: str
    state_secret: bytes
    scope: str = "openid profile email"

    async def _discover(self) -> Dict[str, Any]:
        url = f"https://login.microsoftonline.com/{self.tenant}/v2.0/.well-known/openid-configuration"
        async with RetryingAsyncClient() as c:
            r = await c.get_retry(url, headers={"Accept":"application/json"})
            r.raise_for_status()
            return r.json()

    async def auth_url(self) -> Dict[str, str]:
        disc = await self._discover()
        verifier, challenge = make_pkce_pair()
        state = sign_state(self.state_secret, {"pkce_verifier": verifier, "ts": int(time.time())})
        url = (f'{disc["authorization_endpoint"]}?response_type=code'
               f'&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
               f'&scope={self.scope}&state={state}'
               f'&code_challenge={challenge}&code_challenge_method=S256')
        return {"url": url, "state": state}

    async def exchange(self, code: str, state: str) -> Dict[str, Any]:
        s = verify_state(self.state_secret, state)
        disc = await self._discover()
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": s["pkce_verifier"],
            "client_secret": self.client_secret,
        }
        async with RetryingAsyncClient() as c:
            r = await c.post_retry(disc["token_endpoint"], data=form, headers={"Accept":"application/json"})
            r.raise_for_status()
            tok = r.json()
            jwks = (await c.get_retry(disc["jwks_uri"], headers={"Accept":"application/json"})).json()
        idt = tok["id_token"]
        header = jwt.get_unverified_header(idt)
        key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
        pub = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        claims = jwt.decode(idt, pub, algorithms=[header.get("alg","RS256")],
                            audience=self.client_id, issuer=disc["issuer"])
        email = claims.get("email") or claims.get("preferred_username")
        name  = claims.get("name") or claims.get("given_name")
        return {"issuer":"azure-oidc", "sub": claims["sub"], "email": email, "name": name, "raw": {"tokens": tok}}
