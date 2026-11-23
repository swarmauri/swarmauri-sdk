import asyncio

import pytest


@pytest.mark.perf
def test_mint_perf(token_service, benchmark):
    async def _mint():
        await token_service.mint({"msg": "hi"}, alg="v4.public", kid="ed1")

    benchmark(lambda: asyncio.run(_mint()))
