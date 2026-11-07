import asyncio

import pytest

from swarmauri_agent_realtime._internal.LiveSessionPool import LiveSessionPool


class Session:
    def __init__(self) -> None:
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_concurrent_acquires_share_creation_and_track_leases() -> None:
    pool = LiveSessionPool()
    created = 0

    async def factory() -> Session:
        nonlocal created
        created += 1
        await asyncio.sleep(0)
        return Session()

    first, second = await asyncio.gather(
        pool.acquire("conversation", factory),
        pool.acquire("conversation", factory),
    )

    assert first is second
    assert created == 1
    assert await pool.size() == 1
    await pool.release("conversation")
    await pool.release("conversation", invalidate=True)
    assert first.closed
    assert await pool.size() == 0


@pytest.mark.asyncio
async def test_pool_refuses_to_evict_a_leased_session() -> None:
    pool = LiveSessionPool(max_sessions=1)

    async def factory() -> Session:
        return Session()

    await pool.acquire("first", factory)
    with pytest.raises(RuntimeError, match="currently leased"):
        await pool.acquire("second", factory)
    await pool.close_all()
