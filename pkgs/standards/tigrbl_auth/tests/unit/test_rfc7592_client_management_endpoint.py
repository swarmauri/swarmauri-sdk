"""Endpoint availability tests for RFC 7592 client management."""

import uuid

import httpx
import pytest
from httpx import ASGITransport

from tigrbl_auth.app import app
from tigrbl_auth.routers.surface import surface_api


@pytest.mark.asyncio
async def test_client_management_unknown_client_returns_404():
    await surface_api.initialize()
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        unknown_id = uuid.uuid4()
        resp = await client.patch(
            f"/client/{unknown_id}",
            json={"redirect_uris": "https://b.example/cb"},
        )
    assert resp.status_code == 404
