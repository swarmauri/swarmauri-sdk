import asyncio
from uuid import uuid4

import httpx
import pytest
import uvicorn

from peagen.defaults import DEFAULT_POOL_ID

pytestmark = pytest.mark.infra

GATEWAY_RPC = "http://127.0.0.1:8000/rpc"


async def _wait_for_gateway() -> None:
    async with httpx.AsyncClient() as client:
        for _ in range(50):
            try:
                resp = await client.post(
                    GATEWAY_RPC,
                    json={"jsonrpc": "2.0", "method": "Worker.list", "params": {}},
                )
                if resp.status_code == 200:
                    return
            except Exception:
                pass
            await asyncio.sleep(0.1)
    raise RuntimeError("gateway not ready")


@pytest.fixture(scope="module")
async def running_gateway():
    cfg = uvicorn.Config(
        "peagen.gateway:app", host="127.0.0.1", port=8000, log_level="info"
    )
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())
    await _wait_for_gateway()
    yield
    server.should_exit = True
    await task


@pytest.mark.asyncio
async def test_worker_create_without_auth(running_gateway) -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "Worker.create",
        "params": {
            "id": str(uuid4()),
            "pool_id": str(DEFAULT_POOL_ID),
            "url": "http://127.0.0.1:8001",
            "advertises": {},
            "handlers": {},
        },
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(GATEWAY_RPC, json=payload)
        assert resp.status_code != 403
        assert resp.status_code == 200
