"""Endpoint availability tests for RFC 7592 client management."""

import asyncio

import httpx
import pytest
import uvicorn


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
        "tigrbl_auth.app:app", host="127.0.0.1", port=8005, log_level="warning"
    )
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    await _wait_for_app("http://127.0.0.1:8005")
    try:
        yield "http://127.0.0.1:8005"
    finally:
        server.should_exit = True
        await task


@pytest.mark.asyncio
async def test_client_management_unknown_client_returns_404(running_app):
    base = running_app
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{base}/client/ffffffffffffffff",
            json={"redirect_uris": ["https://b.example/cb"]},
        )
    assert resp.status_code == 404
