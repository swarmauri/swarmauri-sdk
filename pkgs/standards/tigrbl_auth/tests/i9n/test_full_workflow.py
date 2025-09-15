import asyncio
from uuid import UUID

import httpx
import pytest
import uvicorn
import conftest

TENANT_ID = UUID("FFFFFFFF-0000-0000-0000-000000000000")


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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_service_key_introspection_flow(running_app, enable_rfc7662):
    base = running_app
    async with httpx.AsyncClient() as client:
        with conftest.disable_tls_requirement():
            reg_resp = await client.post(
                f"{base}/user/register",
                json={
                    "tenant_slug": "public",
                    "username": "alice",
                    "email": "alice@example.com",
                    "password": "Password123!",
                },
            )
        assert reg_resp.status_code == 201
        tokens = reg_resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        client_resp = await client.post(
            f"{base}/client",
            json={
                "tenant_id": str(TENANT_ID),
                "client_secret": "secret",
                "redirect_uris": ["https://app.example.com/callback"],
            },
            headers=headers,
        )
        assert client_resp.status_code == 201

        service_resp = await client.post(
            f"{base}/service",
            json={"tenant_id": str(TENANT_ID), "name": "example"},
            headers=headers,
        )
        assert service_resp.status_code == 201
        service_id = service_resp.json()["id"]

        key_resp = await client.post(
            f"{base}/servicekey",
            json={"label": "primary", "service_id": service_id},
            headers=headers,
        )
        assert key_resp.status_code == 201
        api_key = key_resp.json()["api_key"]

        introspect_resp = await client.post(
            f"{base}/introspect", data={"token": api_key}
        )
        assert introspect_resp.status_code == 200
        data = introspect_resp.json()
        assert data["active"] is True
        assert data.get("kind") == "service"
