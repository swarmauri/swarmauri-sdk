import asyncio
from uuid import UUID

import httpx
import pytest
import uvicorn

TENANT_ID = UUID("ffffffff-0000-0000-0000-000000000000")


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
    from tigrbl_auth.runtime_cfg import settings

    original = settings.enable_rfc7662
    settings.enable_rfc7662 = True
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
        settings.enable_rfc7662 = original


@pytest.mark.integration
@pytest.mark.asyncio
async def test_service_key_introspection_flow(running_app):
    base = running_app
    async with httpx.AsyncClient() as client:
        user_payload = {
            "tenant_id": str(TENANT_ID),
            "username": "alice",
            "email": "alice@example.com",
            "password": "Passw0rd!",
        }
        user_resp = await client.post(f"{base}/user", json=user_payload)
        assert user_resp.status_code == 201

        client_payload = {
            "tenant_id": str(TENANT_ID),
            "id": "clientapp1",
            "client_secret": "secret",
            "redirect_uris": "https://client.example.com/cb",
        }
        cli_resp = await client.post(f"{base}/client", json=client_payload)
        assert cli_resp.status_code == 201

        svc_payload = {"tenant_id": str(TENANT_ID), "name": "svc1"}
        svc_resp = await client.post(f"{base}/service", json=svc_payload)
        assert svc_resp.status_code == 201
        service_id = svc_resp.json()["id"]

        key_payload = {"label": "test", "service_id": service_id}
        key_resp = await client.post(f"{base}/servicekey", json=key_payload)
        assert key_resp.status_code == 201
        api_key = key_resp.json()["api_key"]

        intro_resp = await client.post(f"{base}/introspect", data={"token": api_key})
        assert intro_resp.status_code == 200
        assert intro_resp.json().get("active") is True
