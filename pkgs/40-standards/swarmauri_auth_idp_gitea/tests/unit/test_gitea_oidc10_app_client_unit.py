import time

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_gitea import GiteaOIDC10AppClient


@pytest.fixture
def client() -> GiteaOIDC10AppClient:
    instance = GiteaOIDC10AppClient(
        issuer="https://gitea.example",
        client_id="client",
        client_secret=SecretStr("secret"),
    )
    instance._discovery = {
        "token_endpoint": "https://gitea.example/token",
    }
    return instance


@pytest.mark.unit
def test_resource(client: GiteaOIDC10AppClient) -> None:
    assert client.resource == "OIDC10AppClient"


@pytest.mark.unit
def test_type(client: GiteaOIDC10AppClient) -> None:
    assert client.type == "GiteaOIDC10AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_cached(client: GiteaOIDC10AppClient) -> None:
    client._cached_token = ("cached", time.time() + 120)
    token = await client.access_token()
    assert token == "cached"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_refreshes(client: GiteaOIDC10AppClient) -> None:
    async def fake_fetch(scope: str | None) -> tuple[str, float]:
        assert scope == "scope-a"
        return "fresh", time.time() + 60

    client._cached_token = None
    client._fetch_token = fake_fetch  # type: ignore[assignment]
    token = await client.access_token("scope-a")
    assert token == "fresh"
