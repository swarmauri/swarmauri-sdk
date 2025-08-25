"""Tests for RFC 7662 token introspection compliance."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.xfail(reason="RFC 7662 compliant token introspection planned")
async def test_introspect_valid_api_key(async_client: AsyncClient, test_api_key):
    """Valid API key should yield an active introspection response."""
    response = await async_client.post(
        "/api_key/introspect", json={"api_key": test_api_key._test_raw_key}
    )
    assert response.status_code == 200
    body = response.json()
    assert "active" in body
    assert body["active"] is True


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.xfail(reason="RFC 7662 compliant token introspection planned")
async def test_introspect_invalid_api_key(async_client: AsyncClient):
    """Invalid API key should yield inactive response per RFC 7662."""
    response = await async_client.post(
        "/api_key/introspect", json={"api_key": "does-not-exist"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "active" in body
    assert body["active"] is False
