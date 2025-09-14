import asyncio

import pytest
from swarmauri_core.crypto.types import JWAAlg


@pytest.mark.perf
def test_mint_performance(benchmark, service) -> None:
    async def _mint() -> None:
        await service.mint({}, alg=JWAAlg.HS256)

    benchmark(lambda: asyncio.run(_mint()))
