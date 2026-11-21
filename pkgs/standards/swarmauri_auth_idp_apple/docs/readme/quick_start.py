from pydantic import SecretBytes
from swarmauri_auth_idp_apple import AppleOAuth21Login

login = AppleOAuth21Login(
    team_id="ABCD123456",
    key_id="XYZ7890",
    client_id="com.example.web",
    private_key_pem=SecretBytes(
        b"""-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"""
    ),
    redirect_uri="https://example.com/callback",
    state_secret=SecretBytes(b"super-secret-state-key"),
)

# In your application, call `await login.auth_url()` to initiate the flow and
# `await login.exchange_and_identity(...)` inside an async context.
print(login.client_id)
