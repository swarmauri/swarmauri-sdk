import asyncio
import json

import pytest
import websockets

from peagen.tui.ws_client import TaskStreamClient


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ws_client_updates_tasks(tmp_path):
    async def handler(websocket):
        await websocket.send(
            json.dumps(
                {
                    "type": "task.update",
                    "data": {"id": "42", "status": "running", "done": 0, "total": 1},
                }
            )
        )
        await websocket.send(
            json.dumps(
                {"type": "worker.update", "data": {"id": "w1", "pool": "default"}}
            )
        )
        await websocket.send(
            json.dumps(
                {"type": "queue.update", "data": {"pool": "default", "length": 1}}
            )
        )
        await asyncio.sleep(0.05)

    server = await websockets.serve(handler, "localhost", 8765)
    client = TaskStreamClient("ws://localhost:8765")
    task = asyncio.create_task(client.listen())
    await asyncio.sleep(0.1)
    task.cancel()
    server.close()
    await server.wait_closed()
    assert "42" in client.tasks
    assert "w1" in client.workers
    assert client.queues.get("default") == 1
