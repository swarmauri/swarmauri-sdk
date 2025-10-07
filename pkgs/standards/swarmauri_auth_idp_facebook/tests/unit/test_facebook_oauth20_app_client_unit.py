import time

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_facebook import FacebookOAuth20AppClient


@pytest.fixture
def client() -> FacebookOAuth20AppClient:
    return FacebookOAuth20AppClient(
        client_id="app-id",
        client_secret=SecretStr("app-secret"),
        graph_base="https://graph.facebook.com",
        version="v19.0",
    )


@pytest.mark.unit
def test_resource_and_type(client: FacebookOAuth20AppClient) -> None:
    assert client.resource == "OAuth20AppClient"
    assert client.type == "FacebookOAuth20AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_fetches_and_caches(
    client: FacebookOAuth20AppClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    responses = [
        {"access_token": "token-1", "expires_in": 120},
        {"access_token": "token-2", "expires_in": 120},
    ]
    calls = []

    async def fake_request(form):
        calls.append(form)
        return responses.pop(0)

    monkeypatch.setattr(client, "_request_token", fake_request)

    token_first = await client.access_token()
    assert token_first == "token-1"
    token_second = await client.access_token()
    assert token_second == "token-1"  # cached
    assert len(calls) == 1

    # Force expiry and ensure a new token is requested
    client._token_cache = ("cached", time.time() - 1)
    token_third = await client.access_token()
    assert token_third == "token-2"
    assert len(calls) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_requires_value(
    client: FacebookOAuth20AppClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def fake_request(form):
        return {"expires_in": 60}

    monkeypatch.setattr(client, "_request_token", fake_request)

    with pytest.raises(ValueError):
        await client.access_token()
