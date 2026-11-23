import time

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_cognito import CognitoOAuth21AppClient


@pytest.fixture
def client() -> CognitoOAuth21AppClient:
    return CognitoOAuth21AppClient(
        base_url="https://cognito.example",
        client_id="client",
        client_secret=SecretStr("secret"),
    )


@pytest.mark.unit
def test_resource(client: CognitoOAuth21AppClient) -> None:
    assert client.resource == "OAuth21AppClient"


@pytest.mark.unit
def test_type(client: CognitoOAuth21AppClient) -> None:
    assert client.type == "CognitoOAuth21AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_cached(client: CognitoOAuth21AppClient) -> None:
    client._cached_token = ("cached", time.time() + 100)
    token = await client.access_token()
    assert token == "cached"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_refreshes(client: CognitoOAuth21AppClient) -> None:
    async def fake_fetch(scope: str | None) -> tuple[str, float]:
        assert scope is None
        return "fresh", time.time() + 60

    client._cached_token = None
    client._fetch_token = fake_fetch  # type: ignore[assignment]
    token = await client.access_token()
    assert token == "fresh"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_credentials_raises() -> None:
    client = CognitoOAuth21AppClient(
        base_url="https://cognito.example",
        client_id="client",
    )
    with pytest.raises(ValueError):
        await client.access_token()
