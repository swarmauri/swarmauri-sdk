"""Endpoint tests for RFC 7591 client registration."""

import asyncio

import httpx
import pytest
import uvicorn
import conftest


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
        "tigrbl_auth.app:app", host="127.0.0.1", port=8003, log_level="warning"
    )
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    await _wait_for_app("http://127.0.0.1:8003")
    try:
        yield "http://127.0.0.1:8003"
    finally:
        server.should_exit = True
        await task


@pytest.mark.asyncio
async def test_rfc7591_client_registration_endpoint(running_app):
    base = running_app
    async with httpx.AsyncClient() as client:
        with conftest.disable_tls_requirement():
            resp = await client.post(
                f"{base}/client/register",
                json={
                    "tenant_slug": "public",
                    "redirect_uris": ["https://a.example/cb"],
                },
            )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_rfc7591_redirect_uris_must_use_https(running_app):
    base = running_app
    async with httpx.AsyncClient() as client:
        with conftest.disable_tls_requirement():
            resp = await client.post(
                f"{base}/client/register",
                json={
                    "tenant_slug": "public",
                    "redirect_uris": ["http://insecure.example/cb"],
                },
            )
    assert resp.status_code == 400
