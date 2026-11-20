import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_google import GoogleOAuth20Login

login = GoogleOAuth20Login(
    client_id="google-client-id",
    client_secret=SecretStr("google-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Redirect the browser to `auth["url"]`, then capture the callback `code` and `state`.
    # Later, call `login.exchange_and_identity(code, state)` inside your callback handler.


asyncio.run(run_flow())
