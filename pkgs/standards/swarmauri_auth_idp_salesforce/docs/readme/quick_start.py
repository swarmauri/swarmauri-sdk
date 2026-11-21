import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_salesforce import SalesforceOAuth20Login

login = SalesforceOAuth20Login(
    base_url="https://login.salesforce.com",
    client_id="salesforce-client-id",
    client_secret=SecretStr("salesforce-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)

# Optional discovery cache when running without network access.
login.discovery_cache = {
    "authorization_endpoint": "https://login.salesforce.com/services/oauth2/authorize",
    "token_endpoint": "https://login.salesforce.com/services/oauth2/token",
    "userinfo_endpoint": "https://login.salesforce.com/services/oauth2/userinfo",
}


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Send the browser to the authorization URL and capture code and state.
    # In the callback, pass code and state to exchange_and_identity.


asyncio.run(run_flow())
