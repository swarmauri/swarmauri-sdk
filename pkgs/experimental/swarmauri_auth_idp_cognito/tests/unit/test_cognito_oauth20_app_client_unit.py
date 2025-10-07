import time

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_cognito import CognitoOAuth20AppClient


@pytest.fixture
def client() -> CognitoOAuth20AppClient:
    return CognitoOAuth20AppClient(
        base_url="https://cognito.example",
        client_id="client",
        client_secret=SecretStr("secret"),
    )


@pytest.mark.unit
def test_resource(client: CognitoOAuth20AppClient) -> None:
    assert client.resource == "OAuth20AppClient"


@pytest.mark.unit
def test_type(client: CognitoOAuth20AppClient) -> None:
    assert client.type == "CognitoOAuth20AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_returns_cached(client: CognitoOAuth20AppClient) -> None:
    client._cached_token = ("cached", time.time() + 100)
    token = await client.access_token()
    assert token == "cached"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_refreshes_cache(client: CognitoOAuth20AppClient) -> None:
    async def fake_fetch(scope: str | None) -> tuple[str, float]:
        assert scope == "scope-a"
        return "fresh", time.time() + 60

    client._fetch_token = fake_fetch  # type: ignore[assignment]
    client._cached_token = ("expired", time.time() - 1)
    token = await client.access_token("scope-a")
    assert token == "fresh"
