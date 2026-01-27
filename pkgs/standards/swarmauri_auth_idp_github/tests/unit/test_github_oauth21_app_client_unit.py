import time
from typing import Any, Dict

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_github import GitHubOAuth21AppClient


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
def client() -> GitHubOAuth21AppClient:
    app_client = GitHubOAuth21AppClient(
        app_id="123",
        installation_id=42,
        private_key_pem=SecretStr("dummy"),
    )
    app_client._app_jwt = lambda: "jwt"  # type: ignore[assignment]
    return app_client


@pytest.mark.unit
def test_resource(client: GitHubOAuth21AppClient) -> None:
    assert client.resource == "OAuth21AppClient"


@pytest.mark.unit
def test_type(client: GitHubOAuth21AppClient) -> None:
    assert client.type == "GitHubOAuth21AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_cached(client: GitHubOAuth21AppClient) -> None:
    payload = {"token": "first", "expires_at": "2099-01-01T00:00:00Z"}
    stub = StubClient(payload)
    client.http_client_factory = lambda: stub  # type: ignore[assignment]
    token_a = await client.access_token()
    token_b = await client.access_token()
    assert token_a == "first"
    assert token_b == "first"
    assert stub.calls == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_refreshes(client: GitHubOAuth21AppClient) -> None:
    payload = {"token": "second", "expires_at": "2099-01-01T00:00:00Z"}
    stub = StubClient(payload)
    client.http_client_factory = lambda: stub  # type: ignore[assignment]
    client.cached_token = ("stale", time.time() - 1)
    token = await client.access_token()
    assert token == "second"
    assert stub.calls == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_scope_not_supported(client: GitHubOAuth21AppClient) -> None:
    with pytest.raises(ValueError):
        await client.access_token("repo")
