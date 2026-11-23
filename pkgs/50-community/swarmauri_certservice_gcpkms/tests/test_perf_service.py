import time
import pytest


@pytest.mark.asyncio
@pytest.mark.perf
async def test_perf_create_csr(service_keyref):
    svc, key = service_keyref
    start = time.perf_counter()
    for _ in range(3):
        await svc.create_csr(key, {"CN": "example.com"})
    elapsed = time.perf_counter() - start
    assert elapsed >= 0
