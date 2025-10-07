import time

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_gitea import GiteaOAuth20AppClient


@pytest.fixture
def client() -> GiteaOAuth20AppClient:
    return GiteaOAuth20AppClient(
        base_url="https://gitea.example",
        client_id="client",
        client_secret=SecretStr("secret"),
    )


@pytest.mark.unit
def test_resource(client: GiteaOAuth20AppClient) -> None:
    assert client.resource == "OAuth20AppClient"


@pytest.mark.unit
def test_type(client: GiteaOAuth20AppClient) -> None:
    assert client.type == "GiteaOAuth20AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_cached(client: GiteaOAuth20AppClient) -> None:
    client._cached_token = ("cached", time.time() + 120)
    token = await client.access_token()
    assert token == "cached"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_refreshes(client: GiteaOAuth20AppClient) -> None:
    async def fake_fetch(scope: str | None) -> tuple[str, float]:
        assert scope == "scope-a"
        return "fresh", time.time() + 60

    client._cached_token = None
    client._fetch_token = fake_fetch  # type: ignore[assignment]
    token = await client.access_token("scope-a")
    assert token == "fresh"
