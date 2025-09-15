"""RFC 7592 client management tests using a live server."""

from __future__ import annotations

import asyncio
from uuid import UUID

import httpx
import pytest
import uvicorn

TENANT_ID = UUID("FFFFFFFF-0000-0000-0000-000000000000")


async def _wait_for_app(base_url: str) -> None:
    """Poll ``/system/healthz`` until the server responds."""
    async with httpx.AsyncClient() as client:
        for _ in range(50):
            try:
                resp = await client.get(f"{base_url}/system/healthz")
                if resp.status_code == 200:
                    return
            except Exception:
                pass
            await asyncio.sleep(0.1)
    raise RuntimeError("server not ready")


@pytest.fixture()
async def running_app(override_get_db):
    from tigrbl_auth.runtime_cfg import settings

    original_tls = settings.require_tls
    settings.require_tls = False
    cfg = uvicorn.Config(
        "tigrbl_auth.app:app", host="127.0.0.1", port=8001, log_level="warning"
    )
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    await _wait_for_app("http://127.0.0.1:8001")
    try:
        yield "http://127.0.0.1:8001"
    finally:
        server.should_exit = True
        await task
        settings.require_tls = original_tls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_client_delete_available(running_app):
    """Clients can be registered and deleted via the service."""
    base = running_app
    async with httpx.AsyncClient() as client:
        reg_resp = await client.post(
            f"{base}/user/register",
            json={
                "tenant_slug": "public",
                "username": "bob",
                "email": "bob@example.com",
                "password": "Password123!",
            },
        )
        assert reg_resp.status_code == 200
        tokens = reg_resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        create_resp = await client.post(
            f"{base}/client/register",
            json={
                "tenant_id": str(TENANT_ID),
                "client_secret": "secret",
                "redirect_uris": ["https://app.example.com/callback"],
            },
            headers=headers,
        )
        assert create_resp.status_code == 201
        client_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"{base}/client/{client_id}", headers=headers)
        assert delete_resp.status_code in (200, 204)

        get_resp = await client.get(f"{base}/client/{client_id}", headers=headers)
        assert get_resp.status_code == 404
