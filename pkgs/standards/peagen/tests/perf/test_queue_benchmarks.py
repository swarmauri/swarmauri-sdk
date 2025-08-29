import asyncio
import os
import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.plugins.queues.redis_queue import RedisQueue


@pytest.mark.perf
def test_in_memory_queue_rpush_blpop(benchmark):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    q = InMemoryQueue()

    async def runner():
        await q.rpush("list", "x")
        await q.blpop(["list"], 0.0)

    benchmark(lambda: loop.run_until_complete(runner()))
    loop.close()
    asyncio.set_event_loop(None)


@pytest.mark.perf
def test_redis_queue_rpush_blpop(benchmark):
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        pytest.skip("REDIS_URL not set")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    q = RedisQueue(uri=redis_url)
    try:
        loop.run_until_complete(q.client.ping())
    except Exception:
        pytest.skip("Redis server not available")

    async def runner():
        await q.rpush("list", "x")
        await q.blpop(["list"], 0.0)

    benchmark(lambda: loop.run_until_complete(runner()))
    loop.run_until_complete(q.client.close())
    loop.close()
    asyncio.set_event_loop(None)
