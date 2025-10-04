from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, sign_state, verify_state

AUTH_SUFFIX = "/services/oauth2/authorize"
TOKEN_SUFFIX = "/services/oauth2/token"

@dataclass(frozen=True)
class SalesforceOAuth20Login:
    \"\"OAuth 2.0 Authorization Code + PKCE for Salesforce (identity via UserInfo or Identity URL).
    \"\"
    base_url: str
    client_id: str
    client_secret: str
    redirect_uri: str
    state_secret: bytes
    scope: str = "refresh_token"     # add 'openid email profile' to use UserInfo

    def _auth_ep(self) -> str: return f"{self.base_url.rstrip('/')}{AUTH_SUFFIX}"
    def _token_ep(self) -> str: return f"{self.base_url.rstrip('/')}{TOKEN_SUFFIX}"

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
            # Try UserInfo first (if OIDC scopes were present)
            try:
                ui = (await c.get_retry(f'{self.base_url.rstrip("/")}/services/oauth2/userinfo',
                                        headers={"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/json"})).json()
                sub = ui.get("sub") or ui.get("user_id")
                name = ui.get("name") or ui.get("preferred_username") or "Unknown"
                email = ui.get("email")
            except Exception:
                # Fallback to Identity URL returned by token response ('id')
                id_url = tok.get("id")
                if not id_url:
                    raise
                ident = (await c.get_retry(id_url, headers={"Authorization": f'Bearer {tok["access_token"]}', "Accept":"application/json"})).json()
                sub = ident.get("user_id") or ident.get("id")
                name = ident.get("display_name") or ident.get("preferred_username") or "Unknown"
                email = ident.get("email") or ident.get("username")
        return {"issuer":"salesforce-oauth2", "sub": sub, "email": email, "name": name, "raw":{"tokens": tok}}
