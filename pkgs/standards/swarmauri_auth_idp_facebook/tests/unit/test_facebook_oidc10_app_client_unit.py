import pytest

from swarmauri_auth_idp_facebook import FacebookOIDC10AppClient


@pytest.fixture
def client() -> FacebookOIDC10AppClient:
    return FacebookOIDC10AppClient()


@pytest.mark.unit
def test_resource_and_type(client: FacebookOIDC10AppClient) -> None:
    assert client.resource == "OIDC10AppClient"
    assert client.type == "FacebookOIDC10AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_not_supported(client: FacebookOIDC10AppClient) -> None:
    with pytest.raises(NotImplementedError):
        await client.access_token()
