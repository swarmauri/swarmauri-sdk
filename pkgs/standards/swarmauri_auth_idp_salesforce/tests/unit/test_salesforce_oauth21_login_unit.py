import json

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_salesforce import SalesforceOAuth21Login


@pytest.fixture
def login() -> SalesforceOAuth21Login:
    instance = SalesforceOAuth21Login(
        base_url="https://login.salesforce.com",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance.discovery_cache = {
        "issuer": "https://login.salesforce.com",
        "authorization_endpoint": "https://login.salesforce.com/services/oauth2/authorize",
        "token_endpoint": "https://login.salesforce.com/services/oauth2/token",
        "userinfo_endpoint": "https://login.salesforce.com/services/oauth2/userinfo",
        "jwks_uri": "https://login.salesforce.com/services/oauth2/certs",
    }
    return instance


@pytest.mark.unit
def test_resource(login: SalesforceOAuth21Login) -> None:
    assert login.resource == "OAuth21Login"


@pytest.mark.unit
def test_type(login: SalesforceOAuth21Login) -> None:
    assert login.type == "SalesforceOAuth21Login"


@pytest.mark.unit
def test_serialization(login: SalesforceOAuth21Login) -> None:
    payload = json.loads(login.model_dump_json())

    restored = SalesforceOAuth21Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret
    restored.discovery_cache = login.discovery_cache

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_uses_discovery(login: SalesforceOAuth21Login) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://login.salesforce.com/services/oauth2/authorize?"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: SalesforceOAuth21Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")
