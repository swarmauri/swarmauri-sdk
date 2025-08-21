import asyncio

import pytest


@pytest.mark.perf
def test_mint_performance(benchmark, service) -> None:
    async def _mint() -> None:
        await service.mint({}, alg="HS256")

    benchmark(lambda: asyncio.run(_mint()))
