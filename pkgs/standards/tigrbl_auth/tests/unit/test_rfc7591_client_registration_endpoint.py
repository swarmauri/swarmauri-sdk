"""RFC 7591 dynamic client registration tests using a live server."""

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
        "tigrbl_auth.app:app", host="127.0.0.1", port=8000, log_level="warning"
    )
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    await _wait_for_app("http://127.0.0.1:8000")
    try:
        yield "http://127.0.0.1:8000"
    finally:
        server.should_exit = True
        await task
        settings.require_tls = original_tls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_client_update_available(running_app):
    """Clients can be registered and updated via the service."""
    base = running_app
    async with httpx.AsyncClient() as client:
        reg_resp = await client.post(
            f"{base}/user/register",
            json={
                "tenant_slug": "public",
                "username": "alice",
                "email": "alice@example.com",
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

        update_resp = await client.patch(
            f"{base}/client/{client_id}",
            json={"grant_types": ["client_credentials"]},
            headers=headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["grant_types"] == ["client_credentials"]
