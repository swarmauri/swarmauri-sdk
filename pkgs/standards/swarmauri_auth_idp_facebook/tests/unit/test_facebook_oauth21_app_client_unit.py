import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_facebook import FacebookOAuth21AppClient


@pytest.fixture
def client() -> FacebookOAuth21AppClient:
    return FacebookOAuth21AppClient(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
    )


@pytest.mark.unit
def test_resource_and_type(client: FacebookOAuth21AppClient) -> None:
    assert client.resource == "OAuth21AppClient"
    assert client.type == "FacebookOAuth21AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_delegates(client: FacebookOAuth21AppClient, monkeypatch):
    async def fake_access_token(self, scope=None):
        return "delegated-token"

    monkeypatch.setattr(
        "swarmauri_auth_idp_facebook.FacebookOAuth20AppClient.access_token",
        fake_access_token,
    )

    token = await client.access_token(scope="ignored")
    assert token == "delegated-token"
