from __future__ import annotations

import json
from importlib import import_module
from typing import Any, Dict, Optional

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_salesforce import SalesforceOAuth20AppClient


oauth20_module = import_module(
    "swarmauri_auth_idp_salesforce.SalesforceOAuth20AppClient"
)


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
        headers: Optional[Dict[str, str]] = None,
    ) -> DummyResponse:
        self._factory.post_calls += 1
        self._factory.last_post_data = dict(data or {})
        payload = self._factory.post_payloads.pop(0)
        return DummyResponse(payload)


class DummyClientFactory:
    def __init__(self, *, post_payloads: Optional[list[Dict[str, Any]]] = None):
        self.post_payloads = list(post_payloads or [])
        self.post_calls = 0
        self.last_post_data: Dict[str, Any] | None = None

    def __call__(self) -> DummyClient:
        return DummyClient(self)


@pytest.fixture
def patch_jwt_encode(monkeypatch: pytest.MonkeyPatch):
    calls: list[Dict[str, Any]] = []

    def fake_encode(payload, key=None, algorithm=None):
        calls.append({"payload": payload, "key": key, "algorithm": algorithm})
        return "encoded-jwt"

    monkeypatch.setattr(oauth20_module.jwt, "encode", fake_encode)
    return calls


@pytest.fixture
def client() -> SalesforceOAuth20AppClient:
    factory = DummyClientFactory(post_payloads=[{"access_token": "token"}])
    return SalesforceOAuth20AppClient(
        token_endpoint="https://login.salesforce.com/services/oauth2/token",
        client_id="client-id",
        user="user@example.com",
        private_key_pem=SecretStr("pem"),
        http_client_factory=factory,
    )


@pytest.mark.unit
def test_resource(client: SalesforceOAuth20AppClient) -> None:
    assert client.resource == "OAuth20AppClient"


@pytest.mark.unit
def test_type(client: SalesforceOAuth20AppClient) -> None:
    assert client.type == "SalesforceOAuth20AppClient"


@pytest.mark.unit
def test_serialization(client: SalesforceOAuth20AppClient) -> None:
    dumped = json.loads(client.model_dump_json())
    cloned = SalesforceOAuth20AppClient.model_construct(**dumped)
    cloned.private_key_pem = client.private_key_pem
    assert cloned.id == client.id
    assert cloned.client_id == client.client_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_access_token_caches(patch_jwt_encode) -> None:
    factory = DummyClientFactory(post_payloads=[{"access_token": "token"}])
    client = SalesforceOAuth20AppClient(
        token_endpoint="https://login.salesforce.com/services/oauth2/token",
        client_id="client-id",
        user="user@example.com",
        private_key_pem=SecretStr("pem"),
        cache_ttl_seconds=120,
        cache_skew_seconds=10,
        http_client_factory=factory,
    )

    token_one = await client.access_token()
    token_two = await client.access_token()

    assert token_one == token_two == "token"
    assert factory.post_calls == 1
    assert len(patch_jwt_encode) == 1
    assert factory.last_post_data["grant_type"] == client.JWT_GRANT


@pytest.mark.unit
def test_requires_private_key() -> None:
    with pytest.raises(
        ValueError,
        match="private key \\(PEM or JWK\\) required for Salesforce JWT bearer flow",
    ):
        SalesforceOAuth20AppClient(
            token_endpoint="https://login.salesforce.com/services/oauth2/token",
            client_id="client-id",
            user="user@example.com",
        )
