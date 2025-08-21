import asyncio

import pytest

from swarmauri_tokens_tlsboundjwt import TlsBoundJWTTokenService


@pytest.mark.perf
def test_mint_perf(benchmark):
    svc = TlsBoundJWTTokenService(None, client_cert_der_getter=lambda: b"perf-cert")

    async def _mint() -> None:
        await svc.mint({"sub": "perf"}, alg="HS256")

    benchmark(lambda: asyncio.run(_mint()))
