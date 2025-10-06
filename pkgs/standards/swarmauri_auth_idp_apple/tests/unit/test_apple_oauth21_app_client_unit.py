import json

import pytest

from swarmauri_auth_idp_apple import AppleOAuth21AppClient


@pytest.fixture
def app_client() -> AppleOAuth21AppClient:
    return AppleOAuth21AppClient()


@pytest.mark.unit
def test_resource(app_client: AppleOAuth21AppClient) -> None:
    assert app_client.resource == "OAuth21AppClient"


@pytest.mark.unit
def test_type(app_client: AppleOAuth21AppClient) -> None:
    assert app_client.type == "AppleOAuth21AppClient"


@pytest.mark.unit
def test_initialization(app_client: AppleOAuth21AppClient) -> None:
    assert isinstance(app_client.id, str)


@pytest.mark.unit
def test_serialization(app_client: AppleOAuth21AppClient) -> None:
    serialized = app_client.model_dump_json()
    data = json.loads(serialized)

    restored = AppleOAuth21AppClient.model_construct(**data)
    assert restored.id == app_client.id
    assert restored.resource == app_client.resource
    assert restored.type == app_client.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_unsupported(app_client: AppleOAuth21AppClient) -> None:
    with pytest.raises(NotImplementedError):
        await app_client.access_token()
