import time
from typing import Any, Dict

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_gitlab import GitLabOAuth21AppClient


class StubResponse:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Dict[str, Any]:
        return self._payload


class StubClient:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload
        self.calls = 0

    async def __aenter__(self) -> "StubClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def post_retry(self, url: str, **_: Any) -> StubResponse:
        self.calls += 1
        return StubResponse(self._payload)


@pytest.fixture
def client() -> GitLabOAuth21AppClient:
    return GitLabOAuth21AppClient(
        base_url="https://gitlab.example",
        client_id="client",
        client_secret=SecretStr("secret"),
    )


@pytest.mark.unit
def test_resource(client: GitLabOAuth21AppClient) -> None:
    assert client.resource == "OAuth21AppClient"


@pytest.mark.unit
def test_type(client: GitLabOAuth21AppClient) -> None:
    assert client.type == "GitLabOAuth21AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_cached(client: GitLabOAuth21AppClient) -> None:
    payload = {"access_token": "first", "expires_in": 3600}
    stub = StubClient(payload)
    client.http_client_factory = lambda: stub  # type: ignore[assignment]
    token_a = await client.access_token()
    token_b = await client.access_token()
    assert token_a == "first"
    assert token_b == "first"
    assert stub.calls == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_refreshes(client: GitLabOAuth21AppClient) -> None:
    payload = {"access_token": "second", "expires_in": 3600}
    stub = StubClient(payload)
    client.http_client_factory = lambda: stub  # type:ignore[assignment]
    client.cached_token = ("stale", time.time() - 1)
    token = await client.access_token()
    assert token == "second"
    assert stub.calls == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_requires_credentials_or_private_key() -> None:
    client = GitLabOAuth21AppClient(
        base_url="https://gitlab.example", client_id="client"
    )
    client.http_client_factory = lambda: None  # type: ignore[assignment]
    with pytest.raises(ValueError):
        await client.access_token()
