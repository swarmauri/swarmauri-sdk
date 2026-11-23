import time

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_gitea import GiteaOAuth21AppClient


@pytest.fixture
def client() -> GiteaOAuth21AppClient:
    return GiteaOAuth21AppClient(
        base_url="https://gitea.example",
        client_id="client",
        client_secret=SecretStr("secret"),
    )


@pytest.mark.unit
def test_resource(client: GiteaOAuth21AppClient) -> None:
    assert client.resource == "OAuth21AppClient"


@pytest.mark.unit
def test_type(client: GiteaOAuth21AppClient) -> None:
    assert client.type == "GiteaOAuth21AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_cached(client: GiteaOAuth21AppClient) -> None:
    client._cached_token = ("cached", time.time() + 120)
    token = await client.access_token()
    assert token == "cached"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_refreshes(client: GiteaOAuth21AppClient) -> None:
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
    client = GiteaOAuth21AppClient(
        base_url="https://gitea.example",
        client_id="client",
    )
    with pytest.raises(ValueError):
        await client.access_token()
