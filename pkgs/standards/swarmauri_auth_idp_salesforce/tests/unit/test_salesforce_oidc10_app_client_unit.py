from __future__ import annotations

import json
from typing import Any, Dict, Optional

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_salesforce import SalesforceOIDC10AppClient


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

    async def get_retry(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> DummyResponse:
        self._factory.get_calls += 1
        self._factory.last_get_url = url
        payload = self._factory.get_payloads.pop(0)
        return DummyResponse(payload)


class DummyClientFactory:
    def __init__(
        self,
        *,
        post_payloads: Optional[list[Dict[str, Any]]] = None,
        get_payloads: Optional[list[Dict[str, Any]]] = None,
    ):
        self.post_payloads = list(post_payloads or [])
        self.get_payloads = list(get_payloads or [])
        self.post_calls = 0
        self.get_calls = 0
        self.last_post_data: Dict[str, Any] | None = None
        self.last_get_url: str | None = None

    def __call__(self) -> DummyClient:
        return DummyClient(self)


@pytest.fixture
def client() -> SalesforceOIDC10AppClient:
    factory = DummyClientFactory(
        get_payloads=[
            {
                "issuer": "https://login.salesforce.com",
                "token_endpoint": "https://login.salesforce.com/services/oauth2/token",
            }
        ]
    )
    return SalesforceOIDC10AppClient(
        issuer="https://login.salesforce.com",
        client_id="client-id",
        user="user@example.com",
        private_key_pem=SecretStr("pem"),
        http_client_factory=factory,
    )


@pytest.mark.unit
def test_resource(client: SalesforceOIDC10AppClient) -> None:
    assert client.resource == "OIDC10AppClient"


@pytest.mark.unit
def test_type(client: SalesforceOIDC10AppClient) -> None:
    assert client.type == "SalesforceOIDC10AppClient"


@pytest.mark.unit
def test_serialization(client: SalesforceOIDC10AppClient) -> None:
    dumped = json.loads(client.model_dump_json())
    cloned = SalesforceOIDC10AppClient.model_construct(**dumped)
    cloned.private_key_pem = client.private_key_pem
    assert cloned.id == client.id
    assert cloned.client_id == client.client_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_discovers_and_reuses_token_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Prepare discovery response
    factory = DummyClientFactory(
        get_payloads=[
            {
                "issuer": "https://login.salesforce.com",
                "token_endpoint": "https://login.salesforce.com/services/oauth2/token",
            }
        ]
    )

    captured_endpoints: list[str] = []

    async def fake_access_token_payload(self, scope=None):
        captured_endpoints.append(self.token_endpoint)
        return {"access_token": "oidc-token"}

    from swarmauri_auth_idp_salesforce import SalesforceOAuth20AppClient as _SF20

    monkeypatch.setattr(_SF20, "access_token_payload", fake_access_token_payload)

    client = SalesforceOIDC10AppClient(
        issuer="https://login.salesforce.com",
        client_id="client-id",
        user="user@example.com",
        private_key_pem=SecretStr("pem"),
        http_client_factory=factory,
    )

    token_one = await client.access_token()
    token_two = await client.access_token()

    assert token_one == token_two == "oidc-token"
    assert factory.get_calls == 1
    assert (
        captured_endpoints == ["https://login.salesforce.com/services/oauth2/token"] * 2
    )
