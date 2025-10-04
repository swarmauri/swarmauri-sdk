from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import jwt
from idp_clients.base.utils_http import RetryingAsyncClient
from idp_clients.base.utils_sec import make_pkce_pair, make_nonce, sign_state, verify_state
from .apple_client_secret import AppleClientSecretFactory

# Apple OAuth 2.0 endpoints (same as OIDC discovery)
AUTH_EP = "https://appleid.apple.com/auth/authorize"
TOKEN_EP = "https://appleid.apple.com/auth/token"
JWKS_URI = "https://appleid.apple.com/auth/keys"

@dataclass(frozen=True)
class AppleOAuth20Login:
    """OAuth 2.0 Authorization Code + PKCE for Apple (verifies ID token; no userinfo endpoint)."""
    team_id: str
    key_id: str
    client_id: str
    private_key_pem: bytes
    redirect_uri: str
    state_secret: bytes
    scope: str = "name email"  # Apple commonly accepts "name email" for OAuth

    async def auth_url(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        nonce = make_nonce()
        state = sign_state(self.state_secret, {"verifier": verifier, "nonce": nonce})
        url = (f'{AUTH_EP}?response_type=code'
               f'&client_id={self.client_id}&redirect_uri={self.redirect_uri}'
               f'&scope={self.scope}&state={state}&nonce={nonce}'
               f'&code_challenge={challenge}&code_challenge_method=S256')
        return {"url": url, "state": state}

    async def exchange_and_identity(self, code: str, state: str) -> Dict[str, Any]:
        s = verify_state(self.state_secret, state)
        client_secret = AppleClientSecretFactory(
            team_id=self.team_id, key_id=self.key_id, client_id=self.client_id, private_key_pem=self.private_key_pem
        ).build()
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": client_secret,
            "code_verifier": s["verifier"],
        }
        async with RetryingAsyncClient() as c:
            tok = (await c.post_retry(TOKEN_EP, data=form, headers={"Accept":"application/json"})).json()
            jwks = (await c.get_retry(JWKS_URI, headers={"Accept":"application/json"})).json()
        idt = tok.get("id_token")
        header = jwt.get_unverified_header(idt)
        key = next((k for k in jwks["keys"] if k["kid"] == header.get("kid")), None)
        pub = jwt.algorithms.ECAlgorithm.from_jwk(key) if key.get("kty") == "EC" else jwt.algorithms.RSAAlgorithm.from_jwk(key)
        claims = jwt.decode(idt, pub, algorithms=[header.get("alg","ES256")],
                            audience=self.client_id, issuer="https://appleid.apple.com")
        if claims.get("nonce") != s["nonce"]:
            raise ValueError("nonce mismatch")
        return {"issuer":"apple-oauth2", "sub": claims["sub"], "email": claims.get("email"), "name": claims.get("name")}
