import asyncio
from uuid import UUID

import httpx
import pytest
import uvicorn

from auto_authn.orm.service_key import ServiceKey

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
    cfg = uvicorn.Config(
        "auto_authn.app:app", host="127.0.0.1", port=8000, log_level="warning"
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
async def test_service_key_workflow(running_app):
    base = running_app
    async with httpx.AsyncClient() as client:
        # create service
        svc_resp = await client.post(
            f"{base}/service",
            json={"tenant_id": str(TENANT_ID), "name": "svc"},
        )
        assert svc_resp.status_code == 201
        service_id = svc_resp.json()["id"]

        # create service key without validity window
        create_payload = {"label": "test", "service_id": service_id}
        key_resp = await client.post(f"{base}/servicekey", json=create_payload)
        assert key_resp.status_code == 201
        body = key_resp.json()

        expected_keys = {
            "id",
            "label",
            "service_id",
            "digest",
            "valid_from",
            "valid_to",
            "last_used_at",
            "created_at",
            "api_key",
        }
        assert set(body) == expected_keys
        assert body["valid_from"] and body["valid_to"]
        assert body["digest"] == ServiceKey.digest_of(body["api_key"])

        # verify persistence and exclusion of api_key
        key_id = body["id"]
        read_resp = await client.get(f"{base}/servicekey/{key_id}")
        assert read_resp.status_code == 200
        read_body = read_resp.json()
        assert "api_key" not in read_body
        assert read_body["digest"] == body["digest"]
        assert read_body["valid_from"] == body["valid_from"]
        assert read_body["valid_to"] == body["valid_to"]

        # valid_from and valid_to are optional but persisted when provided
        custom_from = "2024-01-01T00:00:00+00:00"
        custom_to = "2024-12-31T00:00:00+00:00"
        payload2 = {
            "label": "custom",
            "service_id": service_id,
            "valid_from": custom_from,
            "valid_to": custom_to,
        }
        key_resp2 = await client.post(f"{base}/servicekey", json=payload2)
        assert key_resp2.status_code == 201
        body2 = key_resp2.json()
        assert body2["valid_from"] == custom_from
        assert body2["valid_to"] == custom_to
        read_body2 = (await client.get(f"{base}/servicekey/{body2['id']}")).json()
        assert read_body2["valid_from"] == custom_from
        assert read_body2["valid_to"] == custom_to

        # digest or api_key are not accepted in the request body
        bad_payload = {"label": "bad", "service_id": service_id, "digest": "x"}
        bad_resp = await client.post(f"{base}/servicekey", json=bad_payload)
        assert bad_resp.status_code == 422
        bad_payload2 = {"label": "bad", "service_id": service_id, "api_key": "raw"}
        bad_resp2 = await client.post(f"{base}/servicekey", json=bad_payload2)
        assert bad_resp2.status_code == 422

        # check openapi response example includes validity window
        openapi = (await client.get(f"{base}/openapi.json")).json()
        schema = openapi["components"]["schemas"]["ServiceKeyCreateResponse"]
        assert "valid_from" in schema["properties"]
        assert "valid_to" in schema["properties"]
        example = schema.get("example") or (schema.get("examples") or [{}])[0]
        assert "valid_from" in example and "valid_to" in example
