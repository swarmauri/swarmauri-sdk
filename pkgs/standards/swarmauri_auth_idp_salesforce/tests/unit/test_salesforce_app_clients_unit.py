from importlib import import_module

import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_salesforce import (
    SalesforceOIDC10AppClient,
    SalesforceOAuth20AppClient,
    SalesforceOAuth21AppClient,
)

oauth20_module = import_module(
    "swarmauri_auth_idp_salesforce.SalesforceOAuth20AppClient"
)
oauth21_module = import_module(
    "swarmauri_auth_idp_salesforce.SalesforceOAuth21AppClient"
)
oidc_module = import_module("swarmauri_auth_idp_salesforce.SalesforceOIDC10AppClient")


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self) -> None:  # pragma: no cover - no-op
        return None

    def json(self):
        return self._payload


class DummyClient:
    def __init__(self, factory: "DummyClientFactory"):
        self._factory = factory

    async def __aenter__(self) -> "DummyClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def post_retry(self, url, data=None, headers=None):
        self._factory.post_calls += 1
        self._factory.last_post_data = data
        payload = self._factory.post_payloads.pop(0)
        return DummyResponse(payload)

    async def get_retry(self, url, headers=None):
        self._factory.get_calls += 1
        self._factory.last_get_url = url
        payload = self._factory.get_payloads.pop(0)
        return DummyResponse(payload)


class DummyClientFactory:
    def __init__(self, *, post_payloads=None, get_payloads=None):
        self.post_payloads = list(post_payloads or [])
        self.get_payloads = list(get_payloads or [])
        self.post_calls = 0
        self.get_calls = 0
        self.last_post_data = None
        self.last_get_url = None

    def __call__(self) -> DummyClient:
        return DummyClient(self)


@pytest.fixture
def patch_jwt_encode(monkeypatch):
    calls = []

    def fake_encode(payload, key=None, algorithm=None):
        calls.append({"payload": payload, "key": key, "algorithm": algorithm})
        return "encoded-jwt"

    monkeypatch.setattr(oauth20_module.jwt, "encode", fake_encode)
    return calls


@pytest.mark.unit
def test_oauth20_resource_and_type(patch_jwt_encode) -> None:
    factory = DummyClientFactory(post_payloads=[{"access_token": "token"}])
    client = SalesforceOAuth20AppClient(
        token_endpoint="https://login.salesforce.com/services/oauth2/token",
        client_id="client-id",
        user="user@example.com",
        private_key_pem=SecretStr("pem"),
        http_client_factory=factory,
    )

    assert client.resource == "OAuth20AppClient"
    assert client.type == "SalesforceOAuth20AppClient"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_access_token_caches(monkeypatch, patch_jwt_encode) -> None:
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
def test_oauth20_requires_private_key() -> None:
    with pytest.raises(
        ValueError,
        match="private key \\(PEM or JWK\\) required for Salesforce JWT bearer flow",
    ):
        SalesforceOAuth20AppClient(
            token_endpoint="https://login.salesforce.com/services/oauth2/token",
            client_id="client-id",
            user="user@example.com",
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_delegates_to_oauth20(monkeypatch) -> None:
    captured = []

    async def fake_access_token_payload(self, scope=None):
        captured.append(
            {
                "endpoint": self.token_endpoint,
                "scope": scope,
                "aud": self.aud,
            }
        )
        return {"access_token": "delegated"}

    monkeypatch.setattr(
        oauth21_module.SalesforceOAuth20AppClient,
        "access_token_payload",
        fake_access_token_payload,
    )

    client = SalesforceOAuth21AppClient(
        token_endpoint="https://login.salesforce.com/services/oauth2/token",
        client_id="client-id",
        user="user@example.com",
        private_key_jwk={"kty": "RSA", "n": "modulus", "e": "AQAB"},
        scope="default",
    )

    token = await client.access_token(scope="custom")

    assert token == "delegated"
    assert captured == [
        {
            "endpoint": "https://login.salesforce.com/services/oauth2/token",
            "scope": "custom",
            "aud": None,
        }
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oidc10_discovers_and_reuses_token_client(
    monkeypatch, patch_jwt_encode
) -> None:
    factory = DummyClientFactory(
        get_payloads=[
            {
                "issuer": "https://login.salesforce.com",
                "token_endpoint": "https://login.salesforce.com/services/oauth2/token",
            }
        ]
    )

    captured_endpoints = []

    async def fake_access_token_payload(self, scope=None):
        captured_endpoints.append(self.token_endpoint)
        return {"access_token": "oidc-token"}

    monkeypatch.setattr(
        oidc_module.SalesforceOAuth20AppClient,
        "access_token_payload",
        fake_access_token_payload,
    )

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
