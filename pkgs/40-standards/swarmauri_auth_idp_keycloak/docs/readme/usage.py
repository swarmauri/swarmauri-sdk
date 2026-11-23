import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_keycloak import KeycloakOAuth20Login

login = KeycloakOAuth20Login(
    issuer="https://kc.example.com/realms/myrealm",
    client_id="keycloak-client-id",
    client_secret=SecretStr("keycloak-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)

# Optional: preload discovery metadata when running outside your Keycloak
# instance.
login.discovery_cache = {
    "authorization_endpoint": "https://kc.example.com/realms/myrealm/protocol/openid-connect/auth",
    "token_endpoint": "https://kc.example.com/realms/myrealm/protocol/openid-connect/token",
    "userinfo_endpoint": "https://kc.example.com/realms/myrealm/protocol/openid-connect/userinfo",
}


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Redirect the browser to `auth["url"]`, then capture the callback `code`
    # and `state`.
    # Later, call `login.exchange_and_identity(code, state)` inside your
    # callback handler.


asyncio.run(run_flow())
