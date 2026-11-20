from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_gitea import GiteaOAuth21Login

login = GiteaOAuth21Login(
    base_url="https://gitea.example.com",
    client_id="example-client-id",
    client_secret=SecretStr("example-secret"),
    redirect_uri="https://example.com/callback",
    state_secret=SecretBytes(b"super-secret-state-key"),
)

# Within an async context:
# auth_payload = await login.auth_url()
# identity = await login.exchange_and_identity(code, auth_payload["state"])
print(login.client_id)
