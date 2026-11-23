import asyncio
from swarmauri_auth_idp_aws import AwsOAuth21Login
from pydantic import SecretStr

login = AwsOAuth21Login(
    authorization_endpoint="https://example.awsapps.com/start/oauth2/authorize",
    token_endpoint="https://example.awsapps.com/start/oauth2/token",
    client_id="client-id",
    client_secret=SecretStr("client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=b"aws-workforce-state-key",
)


async def flow() -> None:
    auth = await login.auth_url()
    # Redirect the user to auth["url"], then capture the returned code/state.
    print(auth["url"])


asyncio.run(flow())
