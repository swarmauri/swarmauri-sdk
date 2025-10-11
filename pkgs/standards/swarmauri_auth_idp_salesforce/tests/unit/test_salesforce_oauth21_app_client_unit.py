from __future__ import annotations

import json
from typing import Any, Dict

import pytest

from swarmauri_auth_idp_salesforce import SalesforceOAuth21AppClient


@pytest.fixture
def client() -> SalesforceOAuth21AppClient:
    return SalesforceOAuth21AppClient(
        token_endpoint="https://login.salesforce.com/services/oauth2/token",
        client_id="client-id",
        user="user@example.com",
        private_key_jwk={"kty": "RSA", "n": "modulus", "e": "AQAB"},
    )


@pytest.mark.unit
def test_resource(client: SalesforceOAuth21AppClient) -> None:
    assert client.resource == "OAuth21AppClient"


@pytest.mark.unit
def test_type(client: SalesforceOAuth21AppClient) -> None:
    assert client.type == "SalesforceOAuth21AppClient"


@pytest.mark.unit
def test_serialization(client: SalesforceOAuth21AppClient) -> None:
    dumped = json.loads(client.model_dump_json())
    cloned = SalesforceOAuth21AppClient.model_construct(**dumped)
    # private_key_jwk is a Mapping and should serialize; ensure identity fields match
    assert cloned.id == client.id
    assert cloned.client_id == client.client_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delegates_to_oauth20(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Dict[str, Any]] = []

    async def fake_access_token_payload(self, scope=None):
        captured.append(
            {
                "endpoint": self.token_endpoint,
                "scope": scope,
                "aud": self.aud,
            }
        )
        return {"access_token": "delegated"}

    from swarmauri_auth_idp_salesforce import SalesforceOAuth20AppClient as _SF20

    monkeypatch.setattr(_SF20, "access_token_payload", fake_access_token_payload)

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
