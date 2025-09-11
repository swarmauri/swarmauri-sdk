import asyncio

import httpx
import pytest
import uvicorn

from peagen.worker.base import SWorkerUpdate, WorkerBase
from peagen.defaults import DEFAULT_POOL_ID

GATEWAY_RPC = "http://127.0.0.1:8000/rpc"
WORKER_HEALTH = "http://127.0.0.1:8001/healthz"


class CountingWorker(WorkerBase):
    def __init__(self, *args, max_heartbeats: int = 3, **kwargs) -> None:
        super().__init__(*args, heartbeat_interval=0.2, **kwargs)
        self.max_heartbeats = max_heartbeats
        self.heartbeat_count = 0

    async def _heartbeat_loop(self) -> None:
        for _ in range(self.max_heartbeats):
            await asyncio.sleep(self._hb_every)
            try:
                upd = SWorkerUpdate(
                    id=self.worker_id,
                    pool_id=DEFAULT_POOL_ID,
                    url=self.listen_at,
                    advertises={"cpu": True},
                    handlers={"handlers": list(self._handlers)},
                )
                self._client.call("Worker.update", params=upd.model_dump(mode="json"))
                self.heartbeat_count += 1
            except Exception as exc:  # pragma: no cover
                self.log.warning("heartbeat failed: %s", exc)


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


async def _wait_for_worker() -> None:
    async with httpx.AsyncClient() as client:
        for _ in range(50):
            try:
                resp = await client.get(WORKER_HEALTH)
                if resp.status_code == 200:
                    return
            except Exception:
                pass
            await asyncio.sleep(0.1)
    raise RuntimeError("worker not ready")


@pytest.fixture(scope="module")
async def running_system() -> CountingWorker:
    g_cfg = uvicorn.Config(
        "peagen.gateway:app", host="127.0.0.1", port=8000, log_level="info"
    )
    g_server = uvicorn.Server(g_cfg)
    g_task = asyncio.create_task(g_server.serve())
    await _wait_for_gateway()

    worker = CountingWorker(gateway=GATEWAY_RPC, host="127.0.0.1", port=8001)
    w_cfg = uvicorn.Config(worker.app, host="127.0.0.1", port=8001, log_level="info")
    w_server = uvicorn.Server(w_cfg)
    w_task = asyncio.create_task(w_server.serve())
    await _wait_for_worker()

    yield worker

    w_server.should_exit = True
    g_server.should_exit = True
    await w_task
    await g_task


@pytest.mark.infra
@pytest.mark.asyncio
async def test_01_deployment(running_system: CountingWorker) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GATEWAY_RPC, json={"jsonrpc": "2.0", "method": "Worker.list", "params": {}}
        )
        assert resp.status_code == 200
        resp = await client.get(WORKER_HEALTH)
        assert resp.status_code == 200


@pytest.mark.infra
@pytest.mark.asyncio
async def test_02_worker_registration(running_system: CountingWorker) -> None:
    assert running_system.worker_id is not None
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GATEWAY_RPC, json={"jsonrpc": "2.0", "method": "Worker.list", "params": {}}
        )
        ids = [w["id"] for w in resp.json().get("result", [])]
        assert running_system.worker_id in ids


@pytest.mark.infra
@pytest.mark.asyncio
async def test_03_worker_heartbeats(running_system: CountingWorker) -> None:
    async with httpx.AsyncClient() as client:
        previous = None
        for idx in range(3):
            while running_system.heartbeat_count <= idx:
                await asyncio.sleep(0.05)
            resp = await client.post(
                GATEWAY_RPC,
                json={
                    "jsonrpc": "2.0",
                    "method": "Worker.read",
                    "params": {"id": running_system.worker_id},
                },
            )
            current = resp.json()["result"]["last_seen"]
            assert current != previous
            previous = current
    assert running_system.heartbeat_count >= 3
