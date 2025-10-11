from __future__ import annotations

import json
from typing import Any, Dict, Optional

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_keycloak import KeycloakOAuth20AppClient


class DummyResponse:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    def raise_for_status(self) -> None:  # pragma: no cover - no-op
        return None

    def json(self) -> Dict[str, Any]:
        return self._payload


class DummyClient:
    def __init__(self, factory: "DummyClientFactory"):
        self._factory = factory

    async def __aenter__(self) -> "DummyClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def post_retry(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        auth: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> DummyResponse:
        self._factory.post_calls += 1
        self._factory.last_post_kwargs = {
            "url": url,
            "data": dict(data or {}),
            "auth": auth,
            "headers": dict(headers or {}),
        }
        payload = self._factory.post_payloads.pop(0)
        return DummyResponse(payload)


class DummyClientFactory:
    def __init__(self, *, post_payloads: Optional[list[Dict[str, Any]]] = None):
        self.post_payloads = list(post_payloads or [])
        self.post_calls = 0
        self.last_post_kwargs: Dict[str, Any] | None = None

    def __call__(self) -> DummyClient:
        return DummyClient(self)


@pytest.fixture
def client() -> KeycloakOAuth20AppClient:
    return KeycloakOAuth20AppClient(
        issuer="https://kc.example.com/realms/myrealm",
        client_id="client",
        client_secret=SecretStr("secret"),
    )


@pytest.mark.unit
def test_resource(client: KeycloakOAuth20AppClient) -> None:
    assert client.resource == "OAuth20AppClient"


@pytest.mark.unit
def test_type(client: KeycloakOAuth20AppClient) -> None:
    assert client.type == "KeycloakOAuth20AppClient"


@pytest.mark.unit
def test_serialization(client: KeycloakOAuth20AppClient) -> None:
    dumped = json.loads(client.model_dump_json())
    cloned = KeycloakOAuth20AppClient.model_construct(**dumped)
    cloned.client_secret = client.client_secret
    assert cloned.id == client.id
    assert cloned.client_id == client.client_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_cache_and_endpoint() -> None:
    factory = DummyClientFactory(
        post_payloads=[{"access_token": "a", "expires_in": 3600}]
    )
    client = KeycloakOAuth20AppClient(
        issuer="https://kc.example.com/realms/myrealm",
        client_id="client",
        client_secret=SecretStr("secret"),
        http_client_factory=factory,
    )
    token1 = await client.access_token(scope="scope")
    token2 = await client.access_token()
    assert token1 == token2 == "a"
    assert factory.post_calls == 1
    assert (
        factory.last_post_kwargs["url"]
        == "https://kc.example.com/realms/myrealm/protocol/openid-connect/token"
    )
    assert factory.last_post_kwargs["data"].get("scope") == "scope"
