from pydantic import SecretStr
from swarmauri_auth_idp_azure import AzureOAuth21Login

login = AzureOAuth21Login(
    tenant="organizations",
    client_id="00000000-0000-0000-0000-000000000000",
    client_secret=SecretStr("client-secret"),
    redirect_uri="https://app.example.com/auth/callback",
    state_secret=b"azure-ad-state-key",
)

print(login.client_id)
