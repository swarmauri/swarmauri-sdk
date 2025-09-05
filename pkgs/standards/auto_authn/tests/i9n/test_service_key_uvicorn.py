import asyncio
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest
from httpx import AsyncClient
import uvicorn

from auto_authn.app import app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_service_and_service_key_via_uvicorn_server(override_get_db):
    """Create service and service key through a running Uvicorn server."""
    config = uvicorn.Config(
        app, host="127.0.0.1", port=8001, log_level="warning", loop="asyncio"
    )
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.1)

    try:
        async with AsyncClient(base_url="http://127.0.0.1:8001") as client:
            tenant_payload = {
                "name": "Acme",
                "email": "acme@example.com",
                "slug": "acme",
            }
            res_tenant = await client.post("/tenants", json=tenant_payload)
            assert res_tenant.status_code == 201
            tenant_id = res_tenant.json()["id"]

            service_payload = {"name": "svc", "tenant_id": tenant_id}
            res_service = await client.post("/services", json=service_payload)
            assert res_service.status_code == 201
            service_id = res_service.json()["id"]

            bad = {"label": "bad", "service_id": service_id, "digest": "x"}
            res_bad = await client.post("/service_keys", json=bad)
            assert res_bad.status_code == 422

            now = datetime.now(timezone.utc)
            later = now + timedelta(days=7)
            key_payload = {
                "label": "key1",
                "service_id": service_id,
                "valid_from": now.isoformat(),
                "valid_to": later.isoformat(),
            }
            res_key = await client.post("/service_keys", json=key_payload)
            assert res_key.status_code == 201
            body = res_key.json()
            assert body["label"] == "key1"
            assert body["service_id"] == service_id
            assert body["valid_from"] == key_payload["valid_from"]
            assert body["valid_to"] == key_payload["valid_to"]
            api_key = body["api_key"]
            digest = body["digest"]
            assert digest == sha256(api_key.encode()).hexdigest()

            key_id = body["id"]
            res_get = await client.get(f"/service_keys/{key_id}")
            assert res_get.status_code == 200
            fetched = res_get.json()
            assert fetched["digest"] == digest
            assert "api_key" not in fetched
            assert fetched["valid_from"] == key_payload["valid_from"]
            assert fetched["valid_to"] == key_payload["valid_to"]
    finally:
        server.should_exit = True
        await server_task
