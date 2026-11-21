import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_gitlab import GitLabOAuth20Login

login = GitLabOAuth20Login(
    base_url="https://gitlab.example",
    client_id="gitlab-client-id",
    client_secret=SecretStr("gitlab-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Redirect the browser to `auth["url"]`, then capture the callback `code` and `state`.
    # Later, call `login.exchange_and_identity(code, state)` inside your callback handler.


asyncio.run(run_flow())
