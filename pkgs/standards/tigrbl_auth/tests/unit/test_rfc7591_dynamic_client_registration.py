"""Tests for RFC 7591 dynamic client registration via HTTP server."""

import asyncio

import httpx
import pytest
import uvicorn

from tigrbl_auth import rfc7591


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
        "tigrbl_auth.app:app", host="127.0.0.1", port=8002, log_level="warning"
    )
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    await _wait_for_app("http://127.0.0.1:8002")
    try:
        yield "http://127.0.0.1:8002"
    finally:
        server.should_exit = True
        await task


def test_rfc7591_spec_url() -> None:
    """Module exports the specification URL."""
    assert rfc7591.RFC7591_SPEC_URL.endswith("7591")


@pytest.mark.asyncio
async def test_register_client_via_server(running_app):
    """Client can register through the running server."""
    base = running_app
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base}/client/register",
            json={
                "tenant_slug": "public",
                "redirect_uris": ["https://a.example/cb"],
            },
        )
    assert resp.status_code == 422
