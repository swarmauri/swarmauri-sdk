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
    # Redirect the browser to `auth["url"]`, then capture the callback `code` and `state`.
    # Later, call `login.exchange_and_identity(code, state)` inside your callback handler.


asyncio.run(run_flow())
