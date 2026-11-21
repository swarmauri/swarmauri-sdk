import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_github import GitHubOAuth21Login

login = GitHubOAuth21Login(
    client_id="github-client-id",
    client_secret=SecretStr("github-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Send the browser to the authorization URL and capture code and state.
    # In the callback, pass code and state to exchange_and_identity.


asyncio.run(run_flow())
