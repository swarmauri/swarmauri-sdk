import json

import pytest

from swarmauri_auth_idp_apple import AppleOIDC10AppClient


@pytest.fixture
def app_client() -> AppleOIDC10AppClient:
    return AppleOIDC10AppClient()


@pytest.mark.unit
def test_resource(app_client: AppleOIDC10AppClient) -> None:
    assert app_client.resource == "OIDC10AppClient"


@pytest.mark.unit
def test_type(app_client: AppleOIDC10AppClient) -> None:
    assert app_client.type == "AppleOIDC10AppClient"


@pytest.mark.unit
def test_initialization(app_client: AppleOIDC10AppClient) -> None:
    assert isinstance(app_client.id, str)


@pytest.mark.unit
def test_serialization(app_client: AppleOIDC10AppClient) -> None:
    serialized = app_client.model_dump_json()
    data = json.loads(serialized)

    restored = AppleOIDC10AppClient.model_construct(**data)
    assert restored.id == app_client.id
    assert restored.resource == app_client.resource
    assert restored.type == app_client.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_unsupported(app_client: AppleOIDC10AppClient) -> None:
    with pytest.raises(NotImplementedError):
        await app_client.access_token()
