import asyncio
import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_in_memory_queue_basic_ops():
    q = InMemoryQueue()
    await q.sadd("set", "a")
    assert await q.smembers("set") == ["a"]

    await q.rpush("list", "x")
    await q.rpush("list", "y")
    assert await q.lrange("list", 0, -1) == ["x", "y"]

    item = await q.blpop(["list"], 0.1)
    assert item == ("list", "x")

    await q.rpush("list2", "a")
    await q.rpush("list2", "b")
    item = await q.brpop(["list2"], 0.1)
    assert item == ("list2", "b")

    await q.hset("hash", {"foo": "bar"})
    assert await q.hget("hash", "foo") == "bar"
    await q.expire("hash", 1)
    assert await q.exists("hash")
    await asyncio.sleep(1.1)
    assert not await q.exists("hash")
