"""Tests for RFC 7592 client management operations via server."""

import asyncio

import httpx
import pytest
import uvicorn
import conftest

from tigrbl_auth import rfc7592


async def _wait_for_app(base_url: str) -> None:
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
    cfg = uvicorn.Config(
        "tigrbl_auth.app:app", host="127.0.0.1", port=8004, log_level="warning"
    )
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    await _wait_for_app("http://127.0.0.1:8004")
    try:
        yield "http://127.0.0.1:8004"
    finally:
        server.should_exit = True
        await task


def test_rfc7592_spec_url() -> None:
    """Module exports the specification URL."""
    assert rfc7592.RFC7592_SPEC_URL.endswith("7592")


@pytest.mark.asyncio
async def test_update_and_delete_client_via_server(running_app):
    base = running_app
    async with httpx.AsyncClient() as client:
        with conftest.disable_tls_requirement():
            reg = await client.post(
                f"{base}/client/register",
                json={
                    "tenant_slug": "public",
                    "redirect_uris": ["https://a.example/cb"],
                },
            )
        assert reg.status_code == 201
        client_id = reg.json()["client_id"]
        upd = await client.patch(
            f"{base}/client/{client_id}",
            json={"redirect_uris": ["https://b.example/cb"]},
        )
        assert upd.status_code in {200, 202}
        fetched = await client.get(f"{base}/client/{client_id}")
        assert fetched.status_code == 200
        assert "https://b.example/cb" in fetched.json()["redirect_uris"]
        deleted = await client.delete(f"{base}/client/{client_id}")
        assert deleted.status_code in {200, 204}
        after = await client.get(f"{base}/client/{client_id}")
        assert after.status_code == 404
