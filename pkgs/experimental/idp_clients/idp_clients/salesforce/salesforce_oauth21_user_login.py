from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import jwt
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

AUTH_SUFFIX = "/services/oauth2/authorize"
TOKEN_SUFFIX = "/services/oauth2/token"
USERINFO_SUFFIX = "/services/oauth2/userinfo"   # available when openid scope is used

@dataclass(frozen=True)
class SalesforceOAuth21Login:
    \"\"OAuth 2.1-aligned Authorization Code + PKCE for Salesforce (verifies ID token when present).
    \"\"
    base_url: str                    # login host or My Domain, e.g., https://login.salesforce.com
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes
    scope: str = "openid email profile"

    def _auth_ep(self) -> str: return f"{self.base_url.rstrip('/')}{AUTH_SUFFIX}"
    def _token_ep(self) -> str: return f"{self.base_url.rstrip('/')}{TOKEN_SUFFIX}"
    def _userinfo_ep(self) -> str: return f"{self.base_url.rstrip('/')}{USERINFO_SUFFIX}"

    async def auth_url(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self.state_secret, {"verifier": verifier})
        url = (f'{self._auth_ep()}?response_type=code'
               f'&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
               f'&scope={self.scope}&state={state}'
               f'&code_challenge={challenge}&code_challenge_method=S256')
        return {"url": url, "state": state}

    async def exchange_and_identity(self, code: str, state: str) -> Dict[str, Any]:
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
        # If ID token present, verify via discovery; else fallback to UserInfo
        idt = tok.get("id_token")
        email = None; name = None
        if idt:
            # Fetch discovery to get JWKS
            disc_url = f"{self.base_url.rstrip('/')}/.well-known/openid-configuration"
            async with RetryingAsyncClient() as c2:
                jwks = (await c2.get_retry((await c2.get_retry(disc_url)).json().get("jwks_uri"))).json()
            header = jwt.get_unverified_header(idt)
            key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
            pub = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            claims = jwt.decode(idt, pub, algorithms=[header.get("alg","RS256")],
                                audience=self.client_id, issuer=self.base_url)
            email = claims.get("email"); name = claims.get("name") or "Unknown"
            sub = claims["sub"]
        else:
            # Fall back to UserInfo if scope includes openid
            async with RetryingAsyncClient() as c3:
                ui = (await c3.get_retry(self._userinfo_ep(),
                      headers={"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/json"})).json()
            email = ui.get("email"); name = ui.get("name") or "Unknown"; sub = ui.get("sub") or ui.get("user_id")
        return {"issuer":"salesforce-oauth21", "sub": sub, "email": email, "name": name, "raw":{"tokens": tok}}
