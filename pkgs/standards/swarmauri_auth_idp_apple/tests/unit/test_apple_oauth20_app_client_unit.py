import json

import pytest

from swarmauri_auth_idp_apple import AppleOAuth20AppClient


@pytest.fixture
def app_client() -> AppleOAuth20AppClient:
    return AppleOAuth20AppClient()


@pytest.mark.unit
def test_resource(app_client: AppleOAuth20AppClient) -> None:
    assert app_client.resource == "OAuth20AppClient"


@pytest.mark.unit
def test_type(app_client: AppleOAuth20AppClient) -> None:
    assert app_client.type == "AppleOAuth20AppClient"


@pytest.mark.unit
def test_initialization(app_client: AppleOAuth20AppClient) -> None:
    assert isinstance(app_client.id, str)


@pytest.mark.unit
def test_serialization(app_client: AppleOAuth20AppClient) -> None:
    serialized = app_client.model_dump_json()
    data = json.loads(serialized)

    restored = AppleOAuth20AppClient.model_construct(**data)
    assert restored.id == app_client.id
    assert restored.resource == app_client.resource
    assert restored.type == app_client.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_unsupported(app_client: AppleOAuth20AppClient) -> None:
    with pytest.raises(NotImplementedError):
        await app_client.access_token()
