"""Tests for RFC 7517: JSON Web Key (JWK)."""

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2 import load_signing_jwk, load_public_jwk
from auto_authn.v2.app import jwks, JWKS_PATH


@pytest.mark.unit
def test_jwk_contains_required_fields() -> None:
    priv = load_signing_jwk()
    pub = load_public_jwk()
    assert priv["kty"] == "RSA"
    assert pub["kty"] == "RSA"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jwks_endpoint_serves_rsa_key() -> None:
    app = FastAPI()
    app.add_api_route(JWKS_PATH, jwks)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(JWKS_PATH)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["keys"][0]["kty"] == "RSA"
