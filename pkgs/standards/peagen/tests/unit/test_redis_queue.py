import os
import asyncio
import pytest

from peagen.plugins.queues.redis_queue import RedisQueue


@pytest.mark.unit
@pytest.mark.asyncio
async def test_redis_queue_basic_ops():
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        pytest.skip("REDIS_URL not set")

    q = RedisQueue(uri=redis_url)
    try:
        await q.client.ping()
    except Exception:
        pytest.skip("Redis server not available")
    await q.client.flushdb()

    await q.sadd("set", "a")
    assert sorted(await q.smembers("set")) == ["a"]

    await q.rpush("list", "x")
    await q.rpush("list", "y")
    assert await q.lrange("list", 0, -1) == ["x", "y"]

    await q.rpush("list2", "a")
    await q.rpush("list2", "b")
    item = await q.brpop(["list2"], 0.5)
    assert item == ("list2", "b")

    await q.hset("hash", {"foo": "bar"})
    assert await q.hget("hash", "foo") == "bar"
    await q.expire("hash", 1)
    assert await q.exists("hash")
    await asyncio.sleep(1.1)
    assert not await q.exists("hash")

    await q.client.close()
