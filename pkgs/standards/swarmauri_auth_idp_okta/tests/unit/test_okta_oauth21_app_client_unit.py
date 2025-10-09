from __future__ import annotations

import json
from importlib import import_module
from typing import Any, Dict, Optional

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_okta import OktaOAuth21AppClient


okta_oauth21_module = import_module("swarmauri_auth_idp_okta.OktaOAuth21AppClient")


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
def client() -> OktaOAuth21AppClient:
    return OktaOAuth21AppClient(
        issuer="https://example.okta.com/oauth2/default",
        client_id="client",
        client_secret=SecretStr("secret"),
    )


@pytest.mark.unit
def test_resource(client: OktaOAuth21AppClient) -> None:
    assert client.resource == "OAuth21AppClient"


@pytest.mark.unit
def test_type(client: OktaOAuth21AppClient) -> None:
    assert client.type == "OktaOAuth21AppClient"


@pytest.mark.unit
def test_serialization(client: OktaOAuth21AppClient) -> None:
    dumped = json.loads(client.model_dump_json())
    cloned = OktaOAuth21AppClient.model_construct(**dumped)
    cloned.client_secret = client.client_secret
    assert cloned.id == client.id
    assert cloned.client_id == client.client_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_okta_oauth21_requires_credentials() -> None:
    client = OktaOAuth21AppClient(
        issuer="https://example.okta.com/oauth2/default",
        client_id="client",
    )
    with pytest.raises(ValueError, match="client_secret or private_key_jwk"):
        await client.access_token()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_okta_oauth21_with_client_secret() -> None:
    factory = DummyClientFactory(
        post_payloads=[{"access_token": "secret-token", "expires_in": 60}]
    )
    client = OktaOAuth21AppClient(
        issuer="https://example.okta.com/oauth2/default",
        client_id="client",
        client_secret=SecretStr("secret"),
        http_client_factory=factory,
    )

    token = await client.access_token()
    assert token == "secret-token"
    assert factory.post_calls == 1
    assert factory.last_post_kwargs["auth"] == ("client", "secret")
    assert factory.last_post_kwargs["data"]["grant_type"] == "client_credentials"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_okta_oauth21_private_key_jwt(monkeypatch) -> None:
    factory = DummyClientFactory(
        post_payloads=[{"access_token": "jwt-token", "expires_in": 75}]
    )

    def fake_assertion_body(self: OktaOAuth21AppClient) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "client_assertion_type": "type",
            "client_assertion": "assertion",
        }

    monkeypatch.setattr(
        okta_oauth21_module.OktaOAuth21AppClient,
        "_client_assertion_body",
        fake_assertion_body,
    )

    client = OktaOAuth21AppClient(
        issuer="https://example.okta.com/oauth2/default",
        client_id="client",
        private_key_jwk={"kty": "RSA"},
        http_client_factory=factory,
    )

    token = await client.access_token(scope="okta.scope")
    assert token == "jwt-token"
    assert factory.post_calls == 1
    assert factory.last_post_kwargs["auth"] is None
    assert factory.last_post_kwargs["data"]["client_assertion"] == "assertion"
    assert factory.last_post_kwargs["data"]["scope"] == "okta.scope"
