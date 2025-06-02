# Requires running Redis; mark as integration
import pytest, asyncio, json, websockets
from dqueue.transport.http_api import app, queue
from dqueue.config import settings

pytestmark = pytest.mark.asyncio


async def test_ws_updates(tmp_path):
    async with websockets.connect("ws://localhost:8000/ws/tasks") as ws:
        # push a task
        t = await queue.enqueue("alpha", {"demo": 123})
        msg = json.loads(await ws.recv())
        assert msg["id"] == t.id
