from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_cognito import CognitoOAuth21Login

login = CognitoOAuth21Login(
    issuer="https://example-domain.auth.us-east-1.amazoncognito.com",
    client_id="example-client-id",
    client_secret=SecretStr("example-secret"),
    redirect_uri="https://example.com/callback",
    state_secret=SecretBytes(b"super-secret-state-key"),
)

# Within an async context:
# auth_payload = await login.auth_url()
# identity = await login.exchange_and_identity(code, auth_payload["state"])
print(login.client_id)
