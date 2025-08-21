import time

import pytest


@pytest.mark.perf
@pytest.mark.asyncio
async def test_random_bytes_perf(provider):
    start = time.perf_counter()
    data = await provider.random_bytes(32)
    elapsed = time.perf_counter() - start
    assert len(data) == 32
    assert elapsed < 1.0
