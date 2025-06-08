import pytest
import json
from peagen.plugins.queues.in_memory_queue import InMemoryQueue

@pytest.mark.unit
@pytest.mark.asyncio
async def test_emit_control_pushes():
    q = InMemoryQueue()
    await q.rpush("control_queue", json.dumps({"action": "pause", "label": "x"}))
    cmd = await q.blpop(["control_queue"], 0.1)
    assert cmd == ("control_queue", json.dumps({"action": "pause", "label": "x"}))
