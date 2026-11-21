from pydantic import SecretStr
from swarmauri_auth_idp_facebook import FacebookOAuth21Login

login = FacebookOAuth21Login(
    client_id="1234567890",
    client_secret=SecretStr("app-secret"),
    redirect_uri="https://app.example.com/auth/callback",
    state_secret=b"facebook-state-key",
)

print(login.client_id)
